import unittest
from core.catalog_model_v2 import *
class T(unittest.TestCase):
 def test_multi_supplier(self):
  g=ProductGroup("M99 000001","Velocity 2.0","Работни обувки")
  p=Product("M99 000002",g.m99_id,"PUMA","Velocity 2.0")
  v=Variant("M99 000003",p.m99_id,size="42")
  graph=CommercialProductGraph(g,p,[v],[SupplierProduct(v.m99_id,"SUP1"),SupplierProduct(v.m99_id,"SUP2")])
  self.assertEqual(len(graph.suppliers_for_variant(v.m99_id)),2)
