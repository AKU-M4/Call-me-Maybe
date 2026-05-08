import numpy as np
from abc import ABC, abstractmethod
import functools as ft


class GenerateNumpy():
	def __init__(self, numbers: list[int], add_numbers: list[int]) -> None:
		self.numbers = numbers
		self.add_numbers = add_numbers
	
	@ft.wraps
	def convert(self) -> None:
		np_array = np.array(self.numbers + self.add_numbers)
		min_number = np.min(np_array)
		max_number = np.max(np_array)
		print(np_array)
		print(min_number)
		print(max_number)

def main():
	rnl = [1, 4, 6, 183, 213, 1, 53, 0, 1]
	onl = [1, 2, 4, 5, 6, 15, 1, 53]
	
	tb = GenerateNumpy(rnl, onl)
	
	tb.convert()
main()