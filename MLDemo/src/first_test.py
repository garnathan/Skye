import torch

#z = torch.ones((5, 3), dtype=torch.int16)
#print(z)

torch.manual_seed(1729)
r1 = torch.rand(2, 2)
print(f"A random tensor: {r1}")

r2 = torch.rand(2, 2)
print(f"A different random tensor: {r2}")

torch.manual_seed(1729)
r3 = torch.rand(2, 2)
print(f"Should match r1: {r3 == r1}")