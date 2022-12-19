import numpy as np
import pytest
import os
import sys
import cv2

from source_nomod import Source

img_test = cv2.imread("img/oeil_gris.jpg")

def test_source_init_returns_correct_object():
    """Just to be sure"""
    src = Source(img_test, 10)
    assert(src is not None)

def test_source_img2bin_generates_proper_binary_sequence():
    """Proper = correct length, and all values binary"""
    secrecy_length = 10
    src = Source(img_test, secrecy_length)

    binary_sequence = np.ndarray((1,10), dtype=np.int32)

    src.readimg(binary_sequence)

    assert(binary_sequence.shape == (1,10))
    for i in range(10):
        assert(binary_sequence[0,i] == 0 
               or binary_sequence[0,i] == 1)

def test_source_de2bi_properly_converts_binary_numbers_no_error():
    """Test with a few octal values"""
    src = Source(img_test, 10)

    # valeur 'normale'
    val_1_dec = 4
    val_1_bin = ['0','0','0','0','0','1','0','0']

    # cas limite haut
    val_2_dec = 255
    val_2_bin = ['1','1','1','1','1','1','1','1']

    # cas limite bas
    val_3_dec = 0
    val_3_bin = ['0','0','0','0','0','0','0','0']

    val_1_de2bi = src.de2bi(val_1_dec)
    val_2_de2bi = src.de2bi(val_2_dec)
    val_3_de2bi = src.de2bi(val_3_dec)

    # length comparison
    assert(len(val_1_de2bi) == len(val_1_bin))
    assert(len(val_2_de2bi) == len(val_2_bin))
    assert(len(val_3_de2bi) == len(val_3_bin))

    # element comparison
    for i in range(len(val_1_de2bi)):
        assert(val_1_de2bi[i] == val_1_bin[i])
        assert(val_2_de2bi[i] == val_2_bin[i])
        assert(val_3_de2bi[i] == val_3_bin[i])

def test_source_img2bin_converts_pseudo_image_correctly():
    """Pseudo-image of 2-by-2 pixels"""


    img = np.array([[1,2],[3,4]])

    src = Source(img, 10)

    expected_img2bin = ['0','0','0','0','0','0','0','1', \
                        '0','0','0','0','0','0','1','0', \
                        '0','0','0','0','0','0','1','1', \
                        '0','0','0','0','0','1','0','0']


    # length comparison
    assert(len(src.img_bin) == len(expected_img2bin))

    # element comparison
    for i in range(len(src.img_bin)):
        assert(src.img_bin[i] == expected_img2bin[i])