"""""Export modules for FreeWork data."""

import unittest

from freework_scraper.export.exporter import export_jobs, FreeWorkJob

class TestExportJobs(unittest.TestCase):
    def test_export_jobs(self):
        jobs = [
            FreeWorkJob(
                title="Python Developer",
                company_name="Tech Innovations Inc.",
                location="New York",
                salary=80000,
                remote=True
            ),
            FreeWorkJob(
                title="Data Scientist",
                company_name="Data Science Co.",
                location="San Francisco",
                salary=None,
                remote=False
            )
        ]
        
        output_dir = "test_output"
        export_jobs(jobs, output_dir)
        
        csv_path = Path(output_dir) / "freework_jobs_*.csv"
        xlsx_path = Path(output_dir) / "freework_jobs_*.xlsx"
        
        self.assertTrue(csv_path.exists())
        self.assertTrue(xlsx_path.exists())

if __name__ == '__main__':
    unittest.main()
""