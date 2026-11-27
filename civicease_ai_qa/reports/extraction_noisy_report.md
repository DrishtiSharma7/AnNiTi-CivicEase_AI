# Extraction and audit evaluation (noisy)

> extractor=noisy; documents=48; reference date=2026-11-20; SYNTHETIC data only

## Acceptance gates

| metric | value | rule | pass |
|---|---|---|---|
| field_accuracy | 0.754 | >= 0.9 | False |
| doc_type_accuracy | 1.000 | >= 0.95 | True |
| hallucination_rate | 0.000 | <= 0.05 | True |
| name_mismatch_recall | 1.000 | >= 0.95 | True |
| name_mismatch_precision | 0.182 | >= 0.9 | False |
| expiry_recall | 1.000 | >= 1.0 | True |
| ece | 0.179 | <= 0.15 | False |

## Field Errors

| doc_id | doc_type | condition | field | expected | predicted | status | confidence |
|---|---|---|---|---|---|---|---|
| P01_aadhaar | aadhaar | clear | name | imran sharma | None | missing | 0.950 |
| P01_marksheet | marksheet | clear | name | imran sharma | imran sharm0 | wrong | 0.990 |
| P01_marksheet | marksheet | clear | institution | city polytechnic | city polytechni0 | wrong | 0.990 |
| P02_aadhaar | aadhaar | blurry | id_last4 | 3909 | 3900 | wrong | 0.950 |
| P02_marksheet | marksheet | blurry | name | lakshmi devi | lakshmi dev0 | wrong | 0.990 |
| P02_marksheet | marksheet | blurry | institution | govt senior secondary school | govt senior secondary schoo0 | wrong | 0.990 |
| P03_income_certificate | income_certificate | cropped | name | mohan kumar | mohan kuma0 | wrong | 0.990 |
| P04_aadhaar | aadhaar | lowres | id_last4 | 8657 | 8650 | wrong | 0.950 |
| P04_income_certificate | income_certificate | lowres | annual_income | 240000 | None | missing | 0.950 |
| P04_marksheet | marksheet | lowres | institution | city polytechnic | city polytechni0 | wrong | 0.990 |
| P06_aadhaar | aadhaar | clear | dob | 1998-06-05 | 1998-06-00 | wrong | 0.990 |
| P06_income_certificate | income_certificate | expiring_soon | valid_until | 2026-12-12 | None | missing | 0.950 |
| P07_income_certificate | income_certificate | name_mismatch | annual_income | 300000 | 300001 | wrong | 0.990 |
| P07_income_certificate | income_certificate | name_mismatch | valid_until | 2027-09-13 | 2027-09-10 | wrong | 0.990 |
| P08_aadhaar | aadhaar | missing_field | name | gurpreet khan | None | missing | 0.950 |
| P09_income_certificate | income_certificate | clear | name | gurpreet patel | gurpreet pate0 | wrong | 0.990 |
| P10_aadhaar | aadhaar | blurry | id_last4 | 0268 | 0260 | wrong | 0.950 |
| P10_income_certificate | income_certificate | blurry | valid_until | 2027-08-30 | None | missing | 0.950 |
| P11_income_certificate | income_certificate | cropped | valid_until | 2027-10-11 | None | missing | 0.950 |
| P12_income_certificate | income_certificate | lowres | name | mohan devi | mohan dev0 | wrong | 0.990 |
| P12_income_certificate | income_certificate | lowres | valid_until | 2027-05-10 | 2027-05-11 | wrong | 0.990 |
| P12_marksheet | marksheet | lowres | name | mohan devi | mohan dev0 | wrong | 0.990 |
| P13_aadhaar | aadhaar | clear | name | anil kumar | anil kuma0 | wrong | 0.990 |
| P13_aadhaar | aadhaar | clear | dob | 1954-04-20 | 1990-01-01 | wrong | 0.970 |
| P13_marksheet | marksheet | clear | institution | city polytechnic | city polytechni0 | wrong | 0.990 |
| P14_aadhaar | aadhaar | clear | dob | 1955-03-04 | None | missing | 0.950 |
| P14_aadhaar | aadhaar | clear | id_last4 | 8038 | 8030 | wrong | 0.950 |
| P14_marksheet | marksheet | clear | name | gurpreet singh | gurpreet sing0 | wrong | 0.990 |
| P14_marksheet | marksheet | clear | institution | model degree college | model degree colleg0 | wrong | 0.990 |
| P15_aadhaar | aadhaar | clear | dob | 1969-11-28 | None | missing | 0.950 |
| P16_income_certificate | income_certificate | clear | valid_until | 2027-08-10 | 2027-08-11 | wrong | 0.990 |

## By Condition

| condition | field_accuracy |
|---|---|
| blurry | 0.688 |
| clear | 0.750 |
| cropped | 0.875 |
| expired | 1.000 |
| expiring_soon | 0.833 |
| lowres | 0.625 |
| missing_field | 0.750 |
| name_mismatch | 0.667 |

## Finding Metrics

| code | tp | fp | fn | precision | recall | f1 |
|---|---|---|---|---|---|---|
| EXPIRED | 2 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| EXPIRING_SOON | 1 | 0 | 1 | 1.000 | 0.500 | 0.667 |
| NAME_MISMATCH | 2 | 9 | 0 | 0.182 | 1.000 | 0.308 |
| MISSING_FIELD | 2 | 7 | 0 | 0.222 | 1.000 | 0.364 |
| QUALITY_BLURRY | 12 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| QUALITY_CROPPED | 6 | 0 | 0 | 1.000 | 1.000 | 1.000 |
| LOW_CONFIDENCE | 0 | 0 | 0 | nan | nan | nan |
| DOC_TYPE_UNKNOWN | 0 | 0 | 0 | nan | nan | nan |
