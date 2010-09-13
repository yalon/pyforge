from ut_utils import ForgeTestCase
from forge import UnexpectedSetattr
from contextlib import contextmanager

class MockedClass(object):
    class_variable = 2
    def some_method(self):
        pass

class MockAttributesTest(ForgeTestCase):
    def setUp(self):
        super(MockAttributesTest, self).setUp()
        self.obj = self.forge.create_mock(MockedClass)
    def tearDown(self):
        self.forge.verify()
        self.assertNoMoreCalls()
        super(MockAttributesTest, self).tearDown()
    def test__setting_mock_object_attributes(self):
        attr_value = self.obj.a = object()
        self.assertIs(self.obj.a, attr_value)
        self.forge.replay()
        self.assertIs(self.obj.a, attr_value)
        self.forge.reset()
        with self.assertRaises(AttributeError):
            self.obj.a
    def test__setting_mock_object_attributes_during_replay(self):
        self.forge.replay()
        with self.assertUnexpectedSetattr(self.obj, "a", 2):
            self.obj.a = 2
    def test__setting_mock_object_attributes_during_replay_even_if_set_during_record(self):
        self.obj.a = 2
        self.forge.replay()
        with self.assertUnexpectedSetattr(self.obj, "a", 2):
            self.obj.a = 2
        with self.assertUnexpectedSetattr(self.obj, "a", 3):
            self.obj.a = 3

    def test__getattr_of_nonexisting_attr_during_replay(self):
        self.forge.replay()
        with self.assertRaises(AttributeError):
            self.obj.nonexisting_attr

        with self.assertRaises(AttributeError):
            # a private case of the above, just making a point
            self.obj.nonexisting_method()
    def test__getattr_of_real_methods_during_replay(self):
        self.forge.replay()
        self.obj.some_method
    def test__getattr_of_class_variables_during_record(self):
        self.assertEquals(self.obj.class_variable, MockedClass.class_variable)
    def test__getattr_of_class_variables_during_replay(self):
        self.forge.replay()
        self.assertEquals(self.obj.class_variable, MockedClass.class_variable)
    def test__setattr_of_class_variables_during_record(self):
        self.obj.class_variable = 300
        self.assertEquals(self.obj.class_variable, 300)
        self.forge.replay()
        self.assertEquals(self.obj.class_variable, 300)
    def test__setattr_of_class_variables_during_replay(self):
        self.forge.replay()
        with self.assertUnexpectedSetattr(self.obj, "class_variable", 300):
            self.obj.class_variable = 300
    def test__expect_setattr(self):
        self.obj.__forge__.expect_setattr("a", 666)
        self.forge.replay()
        with self.assertRaises(AttributeError):
            self.obj.a
        self.obj.a = 666
        self.assertEquals(self.obj.a, 666)
    @contextmanager
    def assertUnexpectedSetattr(self, target, name, value):
        with self.assertRaises(UnexpectedSetattr) as caught:
            yield None
        exception = caught.exception
        self.assertIs(exception.got.target, target)
        self.assertEquals(exception.got.name, name)
        self.assertEquals(exception.got.value, value)



