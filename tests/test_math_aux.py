'''
Test functions for the "math_aux" module.
'''

__author__ = ['Miguel Ramos Pernas']
__email__  = ['miguel.ramos.pernas@cern.ch']


# Custom
import hep_spt

# Python
import numpy as np


def test_gcd():
    '''
    Test the function to calculate the greatest common divisor of a set
    of numbers.
    '''
    assert hep_spt.gcd(4, 6) == 2
    assert hep_spt.gcd(4, 6, 8) == 2
    assert np.all(hep_spt.gcd([4, 3], [6, 9]) == [2, 3])


def test_lcm():
    '''
    Test the function to calculate the least common multiple of a set
    of numbers.
    '''
    assert hep_spt.lcm(11, 4) == 44
    assert hep_spt.lcm(8, 4, 2) == 8
    assert np.all(hep_spt.lcm([10, 121], [100, 242]) == [100, 242])


def test_power_2():
    '''
    Test the functions related wih evaluating and creating powers of 2.
    '''
    n = 15

    assert hep_spt.is_power_2(n) == False

    nt = hep_spt.next_power_2(n)

    assert hep_spt.is_power_2(nt) == True
