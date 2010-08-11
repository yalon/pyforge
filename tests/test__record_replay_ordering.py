from ut_utils import ForgeTestCase
from forge import UnexpectedCall

class OrderingTest(ForgeTestCase):
    def setUp(self):
        super(OrderingTest, self).setUp()
        self.stub = self.forge.create_function_stub(lambda arg: None)
class StrictOrderingTest(OrderingTest):
    def test__strict_ordering(self):
        self.stub(1)
        self.stub(2)
        self.forge.replay()
        with self.assertRaises(UnexpectedCall) as caught:
            self.stub(2)
        self.assertIs(caught.exception.got.target, self.stub)
        self.assertIs(caught.exception.expected.target, self.stub)
class OrderGroupsTest(OrderingTest):
    def setUp(self):
        super(OrderGroupsTest, self).setUp()
        with self.forge.any_order():
            self.stub(0)
            self.stub(1)
        self.stub(2)
        self.stub(3)
        with self.forge.any_order():
            self.stub(4)
            self.stub(5)
        self.forge.replay()
    def test__as_recorded(self):
        for i in range(6):
            self.stub(i)
        self.forge.verify()
    def test__not_as_recorded(self):
        self.stub(1)
        self.stub(0)
        self.stub(2)
        self.stub(3)
        self.stub(5)
        self.stub(4)
        self.forge.verify()

