import unittest
from engine import *
class T(unittest.TestCase):
 def test_demand(self): self.assertAlmostEqual(demand(1,5,1,.8,10)["volume_m3d"],62.5)
 def test_density(self): self.assertAlmostEqual(density(2,2),2500)
 def test_hf(self): self.assertGreater(hf_hw(5,100,63,150),0)
 def test_green(self): self.assertEqual(water_status(300,10,5,"Permanente",30)[0],"VERDE")
 def test_red(self): self.assertEqual(water_status(30,2,5,"Permanente",10)[0],"ROJO")
 def test_gray(self): self.assertEqual(water_status(30,10,5,"Desconocido",10)[0],"GRIS")
 def test_sprinkler(self): self.assertAlmostEqual(sprinkler_spacing(20,2)[0],12)
 def test_sector(self): self.assertEqual(sectors_needed(10,3),4)
 def test_velocity(self): self.assertGreater(hydraulics(5,100,63,150,10,15)["velocity_ms"],0)
 def test_bad(self):
  with self.assertRaises(ValueError): demand(0,5,1,.8,10)
if __name__=="__main__":unittest.main()
