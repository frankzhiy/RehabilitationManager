
import pandas as pd
from django.core.management.base import BaseCommand
from prescription.models import MotionList

class Command(BaseCommand):
    help = 'Replace MotionList table content with data from motionlist.xlsx'

    def handle(self, *args, **kwargs):
        # Read the Excel file
        df = pd.read_excel('motionlist.xlsx')

        # Clear existing data in the MotionList table
        MotionList.objects.all().delete()

        # Insert new data
        for _, row in df.iterrows():
            MotionList.objects.create(
                action_id=row['action_id'],
                name=row['name'],
                category=row['category'],
                is_recommended=row['is_recommended'],
                weekly_training_count=row['weekly_training_count'],
                daily_training_count=row['daily_training_count'],
                sets_per_session=row['sets_per_session'],
                reps_per_set=row['reps_per_set'],
                training_method=row['training_method'],
                intensity=row['intensity'],
                duration=row['duration'],
                object=row['object'],
                applicability=row['applicability'],
                purpose=row['purpose'],
                details=row['details']  # Directly assign the value
            )

        self.stdout.write(self.style.SUCCESS('Successfully replaced MotionList table content'))