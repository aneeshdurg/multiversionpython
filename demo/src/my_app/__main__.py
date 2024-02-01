import importshim

import dep_a
import dep_b

print("from pd@2.2.0:", dep_a.get_data())
print("from pd@2.0.3:", dep_b.get_data())
