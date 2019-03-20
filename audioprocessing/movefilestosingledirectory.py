import shutil
import os
import itertools


sliced = "/Volumes/G-DRIVE with Thunderbolt/Reframed1_Audio/sliced"
flat = "/Volumes/G-DRIVE with Thunderbolt/Reframed1_Audio/flat"

os.chdir(sliced)
a = list(os.walk("."))


for dirname, _, files in a:
	for f in files:
		shutil.copyfile(os.path.join(dirname,f), os.path.join(flat, dirname+"___"+f))

