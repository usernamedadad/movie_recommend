import pandas as pd
from django.core.management.base import BaseCommand
from movies.models import Movie
import os

class Command(BaseCommand):
    help = 'Import movies from CSV'

    def handle(self, *args, **options):
        # Assuming the CSV is in the project root (d:\project_new)
        # Since manage.py is in d:\project_new, this relative path should work
        file_path = 'tmdb_movies_2000.csv'
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"File {file_path} not found"))
            return

        try:
            df = pd.read_csv(file_path)
            # Fill NaN with empty string for string fields, 0 for numeric
            df['star'] = pd.to_numeric(df['star'], errors='coerce').fillna(0.0)
            df = df.fillna('')
            
            count = 0
            for index, row in df.iterrows():
                try:
                    Movie.objects.update_or_create(
                        id=row['id'],
                        defaults={
                            'title': row['title'],
                            'image_link': row['image_link'],
                            'country': row['country'],
                            'years': str(row['years']).replace('.0', ''), # Handle float years if any
                            'director_description': row['director_description'],
                            'leader': row['leader'],
                            'star': row['star'],
                            'description': row['description'],
                            'alltags': row['alltags'],
                            'imdb': row['imdb'],
                            'language': row['language'],
                            'time_length': row['time_length'],
                        }
                    )
                    count += 1
                    if count % 100 == 0:
                        self.stdout.write(f"Imported {count} movies...")
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error importing movie {row.get('title', 'Unknown')}: {e}"))
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} movies'))
        except Exception as e:
             self.stdout.write(self.style.ERROR(f"Error reading CSV: {e}"))
