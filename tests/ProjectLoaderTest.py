from source.loaders import ProjectLoader
import unittest

class ProjectLoaderTest(unittest.TestCase):
    
    def setUp(self):
        self.loader = ProjectLoader()
        
    def test_load_project_name_with_suffix(self):
        self.project_path = 'resources/empty_project_with.suffix'
        self.project_name = 'empty_project_with'
        self.assertEqual(self.loader.load_project(self.project_path).name, self.project_name)
    
    def test_load_project_name(self):
        self.project_path = 'resources/empty_project'
        self.project_name = 'empty_project'
        self.assertEqual(self.loader.load_project(self.project_path).name, self.project_name)
        

if __name__ == '__main__':
    unittest.main()