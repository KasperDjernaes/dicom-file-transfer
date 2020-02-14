# anonymize.py
"""Read a dicom file (or directory of files), partially "anonymize" it (them),
by replacing Person names, patient id, optionally remove curves
and private tags, and write result to a new file (directory)
This is an example only; use only as a starting point.
"""
# Copyright (c) 2008-2012 Darcy Mason
# This file is part of pydicom, relased under an MIT license.
#    See the file license.txt included with this distribution, also
#    available at http://pydicom.googlecode.com
# Use at your own risk!!
# Many more items need to be addressed for proper de-identifying DICOM data.
# In particular, note that pixel data could have confidential data "burned in"
# Annex E of PS3.15-2011 DICOM standard document details what must be done to
# fully de-identify DICOM data

from __future__ import print_function

usage = """
Usage:
python anonymize.py dicomfile.dcm outputfile.dcm
OR
python anonymize.py originals_directory anonymized_directory

Note: Use at your own risk. Does not fully de-identify the DICOM data as per
the DICOM standard, e.g in Annex E of PS3.15-2011.
"""

import os
import os.path
import dicom


def anonymize(filename, output_filename, new_person_name="anonymous",
              new_patient_id="id", remove_curves=True, remove_private_tags=True):
    """Replace data element values to partly anonymize a DICOM file.
    Note: completely anonymizing a DICOM file is very complicated; there
    are many things this example code does not address. USE AT YOUR OWN RISK.
    """

    # Define call-back functions for the dataset.walk() function
    def PN_callback(ds, data_element):
        """Called from the dataset "walk" recursive function for all data elements."""
        if data_element.VR == "PN":
            data_element.value = new_person_name

    def curves_callback(ds, data_element):
        """Called from the dataset "walk" recursive function for all data elements."""
        if data_element.tag.group & 0xFF00 == 0x5000:
            del ds[data_element.tag]

    # Load the current dicom file to 'anonymize'
    dataset = dicom.read_file(filename)

    # Remove patient name and any other person names
    dataset.walk(PN_callback)

    # Change ID
    dataset.PatientID = new_patient_id

    # Remove data elements (should only do so if DICOM type 3 optional)
    # Use general loop so easy to add more later
    # Could also have done: del ds.OtherPatientIDs, etc.
    for name in ['OtherPatientIDs', 'OtherPatientIDsSequence']:
        if name in dataset:
            delattr(dataset, name)

    # Same as above but for blanking data elements that are type 2.
    for name in ['PatientBirthDate']:
        if name in dataset:
            dataset.data_element(name).value = ''

    # Remove private tags if function argument says to do so. Same for curves
    if remove_private_tags:
        dataset.remove_private_tags()
    if remove_curves:
        dataset.walk(curves_callback)

    # write the 'anonymized' DICOM out under the new filename
    dataset.save_as(output_filename)