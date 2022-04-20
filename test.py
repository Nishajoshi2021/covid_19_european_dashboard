from django.test import TestCase
import json

class TestCalls(TestCase):

  def test_get_countries(self):
    response=self.client.get('/getcountries', follow=True)
    response_data=json.loads(response.content)
    self.assertEqual(len(response_data),51)

  def test_compareddate(self):
    response=self.client.get('/getcompareddata', {'country1': 'Ireland', 'country2': 'Germany', 'casespermillion': 'false', 'chartvariable': 'total_cases'})

    response_data=json.loads(response.content)
    #print(len(response_data))
    self.assertEqual(len(response_data), 2)
    self.assertNotEqual(len(response_data[0]), 0)
    self.assertNotEqual(len(response_data[1]), 0)

  def test_total_deaths_linear_regression(self):
    response=self.client.get('/total_deaths_linear_regression', {'country': 'Ireland'})
    response_data = json.loads(response.content)
    self.assertEqual(len(response_data.keys()), 3)
    self.assertGreater(len(response_data['date']),0)
    self.assertGreater(len(response_data['actual']), 0)
    self.assertGreater(len(response_data['predicted']), 0)

  def test_trends_data_analysis(self):
    response=self.client.get('/trends_data_analysis', {'country':'Italy'})
    response_data = json.loads(response.content)
    self.assertEqual(len(response_data.keys()), 4)
    self.assertGreater(len(response_data['date_7_days']), 0)
    self.assertEqual(len(response_data['new_cases_trends'].keys()), 5)
    self.assertEqual(len(response_data['new_deaths_trends'].keys()), 5)
    self.assertEqual(len(response_data['new_vaccinations_trends'].keys()), 5)
    self.assertGreater(len(response_data['new_cases_trends']['7_days_data']), 0)
    self.assertGreater(len(response_data['new_deaths_trends']['7_days_data']), 0)
    self.assertGreater(len(response_data['new_vaccinations_trends']['7_days_data']), 0)
    self.assertGreater((response_data['new_cases_trends']['7_days_average']), -1)
    self.assertGreater((response_data['new_deaths_trends']['7_days_average']), -1)
    self.assertGreater((response_data['new_vaccinations_trends']['7_days_average']), -1)

  def test_countries_map_data(self):
    response=self.client.get('/countries_map_data')
    response_data = json.loads(response.content)
    self.assertEqual(len(response_data.keys()),51)
    self.assertEqual(len(response_data['Ireland'].keys()), 3)
    self.assertEqual(response_data['Ireland']['coords']['lat'], 53.41)
    self.assertEqual(response_data['Ireland']['coords']['lng'], -8.24)
    self.assertGreater(response_data['Ireland']['total_deaths'], 0)
    self.assertGreater(response_data['Ireland']['total_cases'], 0)





