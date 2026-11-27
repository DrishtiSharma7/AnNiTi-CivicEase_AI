# Defect drafts (from the latest evaluation reports)

Each item needs a human decision: rule or code bug, labelling mistake, or accepted limitation.

### Extraction errors (noisy) (31)
Reproduce: `python run_extraction_eval.py --extractor noisy   (documents are under data/documents/)`

- doc_id=P01_aadhaar, field=name, expected=imran sharma, predicted=, status=missing, confidence=0.95
- doc_id=P01_marksheet, field=name, expected=imran sharma, predicted=imran sharm0, status=wrong, confidence=0.99
- doc_id=P01_marksheet, field=institution, expected=city polytechnic, predicted=city polytechni0, status=wrong, confidence=0.99
- doc_id=P02_aadhaar, field=id_last4, expected=3909, predicted=3900, status=wrong, confidence=0.95
- doc_id=P02_marksheet, field=name, expected=lakshmi devi, predicted=lakshmi dev0, status=wrong, confidence=0.99
- doc_id=P02_marksheet, field=institution, expected=govt senior secondary school, predicted=govt senior secondary schoo0, status=wrong, confidence=0.99
- doc_id=P03_income_certificate, field=name, expected=mohan kumar, predicted=mohan kuma0, status=wrong, confidence=0.99
- doc_id=P04_aadhaar, field=id_last4, expected=8657, predicted=8650, status=wrong, confidence=0.95
- doc_id=P04_income_certificate, field=annual_income, expected=240000, predicted=, status=missing, confidence=0.95
- doc_id=P04_marksheet, field=institution, expected=city polytechnic, predicted=city polytechni0, status=wrong, confidence=0.99
- doc_id=P06_aadhaar, field=dob, expected=1998-06-05, predicted=1998-06-00, status=wrong, confidence=0.99
- doc_id=P06_income_certificate, field=valid_until, expected=2026-12-12, predicted=, status=missing, confidence=0.95
- doc_id=P07_income_certificate, field=annual_income, expected=300000, predicted=300001, status=wrong, confidence=0.99
- doc_id=P07_income_certificate, field=valid_until, expected=2027-09-13, predicted=2027-09-10, status=wrong, confidence=0.99
- doc_id=P08_aadhaar, field=name, expected=gurpreet khan, predicted=, status=missing, confidence=0.95
- doc_id=P09_income_certificate, field=name, expected=gurpreet patel, predicted=gurpreet pate0, status=wrong, confidence=0.99
- doc_id=P10_aadhaar, field=id_last4, expected=0268, predicted=0260, status=wrong, confidence=0.95
- doc_id=P10_income_certificate, field=valid_until, expected=2027-08-30, predicted=, status=missing, confidence=0.95
- doc_id=P11_income_certificate, field=valid_until, expected=2027-10-11, predicted=, status=missing, confidence=0.95
- doc_id=P12_income_certificate, field=name, expected=mohan devi, predicted=mohan dev0, status=wrong, confidence=0.99
- doc_id=P12_income_certificate, field=valid_until, expected=2027-05-10, predicted=2027-05-11, status=wrong, confidence=0.99
- doc_id=P12_marksheet, field=name, expected=mohan devi, predicted=mohan dev0, status=wrong, confidence=0.99
- doc_id=P13_aadhaar, field=name, expected=anil kumar, predicted=anil kuma0, status=wrong, confidence=0.99
- doc_id=P13_aadhaar, field=dob, expected=1954-04-20, predicted=1990-01-01, status=wrong, confidence=0.97
- doc_id=P13_marksheet, field=institution, expected=city polytechnic, predicted=city polytechni0, status=wrong, confidence=0.99
- doc_id=P14_aadhaar, field=dob, expected=1955-03-04, predicted=, status=missing, confidence=0.95
- doc_id=P14_aadhaar, field=id_last4, expected=8038, predicted=8030, status=wrong, confidence=0.95
- doc_id=P14_marksheet, field=name, expected=gurpreet singh, predicted=gurpreet sing0, status=wrong, confidence=0.99
- doc_id=P14_marksheet, field=institution, expected=model degree college, predicted=model degree colleg0, status=wrong, confidence=0.99
- doc_id=P15_aadhaar, field=dob, expected=1969-11-28, predicted=, status=missing, confidence=0.95
- doc_id=P16_income_certificate, field=valid_until, expected=2027-08-10, predicted=2027-08-11, status=wrong, confidence=0.99
