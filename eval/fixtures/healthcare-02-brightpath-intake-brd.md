# Business Requirements Document: Patient Intake and Prior Authorisation Assistant

**Organisation:** Brightpath Orthopaedic Group (fictional)
**Document owner:** Cordelia Aubrey-Finch, director of patient access
**Version:** 1.1
**Contact:** patientaccess@brightpath.example.com

## 1. Context

Brightpath Orthopaedic Group is a healthcare provider with five surgical centres and 38 surgeons. Patients are referred by primary care doctors, and most procedures need prior authorisation from the patient's insurer before surgery can be scheduled. The authorisation process is slow and manual, and it is the single largest cause of surgery delays.

## 2. Current pain points

- Referral packets arrive by fax, portal upload and email. They are scanned PDFs of varying quality. Intake coordinators retype demographics, diagnosis codes and clinical notes into the record system.
- Preparing an authorisation request takes an average of 42 minutes of coordinator time, and about 1 in 4 requests is returned by the insurer for missing documentation.
- Median time from referral to authorised surgery date is 19 days. Patients call repeatedly to ask for a status.
- Coordinators keep a personal checklist of what each insurer requires, and the checklists differ and go out of date.

## 3. Objectives

1. Reduce coordinator time per authorisation request from 42 to 15 minutes.
2. Reduce insurer returns for missing documentation from 25 percent to below 8 percent.
3. Reduce median referral to authorised date from 19 to 10 days.
4. Provide patients with accurate status without a phone call.

## 4. Must-have capabilities

1. **Referral packet extraction.** Read a scanned referral and extract patient demographics, referring provider, diagnosis, procedure, and relevant clinical history into a structured form, with a confidence flag for each field and a link to the page it came from.
2. **Insurer requirement checklist.** For a given insurer and procedure, list the documents and clinical criteria required, compare them to what the packet contains, and highlight what is missing before submission.
3. **Authorisation letter drafting.** Draft the medical necessity narrative from the clinical notes, for the coordinator and the surgeon to review and sign. Nothing is submitted without a human sign-off.
4. **Status tracker with patient updates.** A board of requests by stage (received, incomplete, submitted, pending insurer, approved, denied) and plain-language status messages that staff can send to the patient.

## 5. Should-have capabilities

- Denial reason analysis with a suggested appeal outline.
- Weekly dashboard of turnaround time by insurer and by surgeon.

## 6. Compliance and security

- The proof of concept shall use only synthetic referral packets. No real patient information may be loaded.
- In production, all processing of patient information must happen under agreements that satisfy the applicable health privacy regulation.
- All extracted fields and drafted letters shall be stored with an audit trail of who edited what.
- The system must never state a clinical conclusion that does not appear in the source documents.

## 7. Budget and timeline

- The steering group has approved 65,000 dollars for the discovery and proof of concept phase.
- Prototype demonstration to the steering group on the second Tuesday of October.
- Pilot at one surgical centre in the first quarter of next year, subject to a separate budget.

## 8. Success criteria

- Field extraction accuracy of at least 90 percent on 60 synthetic packets, scored by coordinators.
- The checklist correctly identifies missing items in at least 85 percent of test packets.
- Drafted narratives are rated acceptable or better by two surgeons in at least 80 percent of cases.

## 9. Action items

| Action | Owner | Due |
|--------|-------|-----|
| Prepare 60 synthetic referral packets, including poor-quality scans | Marguerite Oduya, intake supervisor | 6 September |
| Document requirements for the top five insurers and ten procedures | Cordelia Aubrey-Finch | 13 September |
| Nominate two surgeons for narrative review | Dr. Ignatius Ferreira-Bloom, chief of surgery | 20 September |
| Obtain approval from the privacy officer for the synthetic data approach | Sabine Rotheram, privacy officer | 27 September |
| Share architecture outline and cost table | Supplier | 4 October |

## 10. Risks

- Poor scan quality could lower extraction accuracy. Mitigation: include difficult scans in the test set and flag low-confidence fields for review.
- Insurer rules change frequently. Mitigation: keep the rules in an editable table, not in code.
- Surgeons may not trust drafted narratives. Mitigation: show the source passages for every statement.
