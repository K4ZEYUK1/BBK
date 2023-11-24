from users.models import Province, StandardHoliday
import holidays
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generates Holidays from 1990 to 2050"

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        german_states = [
            'BW', 'BY', 'BE', 'BB', 'HB', 'HH', 'HE', 'MV',
            'NI', 'NW', 'RP', 'SL', 'SN', 'ST', 'SH', 'TH'
        ]

        german_state_mapping = {
            'BW': 'Baden-Württemberg',
            'BY': 'Bayern',
            'BE': 'Berlin',
            'BB': 'Brandenburg',
            'HB': 'Bremen',
            'HH': 'Hamburg',
            'HE': 'Hessen',
            'MV': 'Mecklenburg-Vorpommern',
            'NI': 'Niedersachsen',
            'NW': 'Nordrhein-Westfalen',
            'RP': 'Rheinland-Pfalz',
            'SL': 'Saarland',
            'SN': 'Sachsen',
            'ST': 'Sachsen-Anhalt',
            'SH': 'Schleswig-Holstein',
            'TH': 'Thüringen'
        }

        for state in german_states:
            new_state = Province(country='DE', state_abreviation=state, name=german_state_mapping[state])
            new_state.save()

            output_line = "Generated" + new_state.name

            self.stdout.write(output_line)

            for holiday_date, name in sorted(holidays.Germany(years=range(1990, 2050), prov=state, language='de').items()):
                new_holiday = StandardHoliday(name=name, country='DE', date=holiday_date,
                                              province=Province.objects.get(state_abreviation=state))
                new_holiday.save()

                output_line_loop = "Generated" + new_holiday.name

                self.stdout.write(output_line_loop)
