# Business Requirements Document: Dock Scheduling Assistant

**Client:** Harbourline Cold Storage (fictional)
**Prepared by:** Ostrava Bridge Advisory (fictional)
**Version:** 0.3 draft
**Contact:** programmes@harbourline.example.com

## 1. Background

Harbourline Cold Storage operates three temperature-controlled warehouses on the east coast. Each site receives between 60 and 110 inbound trucks a day, mostly chilled and frozen food. Dock doors are booked by carriers through a shared spreadsheet and a booking inbox. The logistics sector is under heavy pressure on dwell time, and every hour a refrigerated trailer waits in the yard costs money and puts product at risk.

## 2. Problem statement

- Carriers book dock slots by email. Planners copy the details into a spreadsheet by hand, which takes about two hours per site per day.
- Around 22 percent of inbound trucks arrive outside their booked window. A late truck blocks a door that a later truck needs.
- Average yard dwell time is 94 minutes. The target is under 60 minutes.
- Pallet counts and temperature classes are only known when the truck arrives, so door assignment is a guess.
- Detention charges paid to carriers because of our delays reached an estimated 310,000 in the last financial year.

## 3. Goals

1. Cut average yard dwell time from 94 to under 60 minutes within two quarters of rollout.
2. Reduce manual booking entry time by at least 80 percent.
3. Reduce detention charges by 35 percent in the first year.
4. Give planners a single live view of doors, trucks and expected arrivals.

## 4. Must-have features

1. **Booking intake from email.** Read carrier booking emails and attachments, extract carrier, purchase order, pallet count, temperature class and requested window, and create a draft booking for planner confirmation.
2. **Dock door allocation board.** A timeline board of doors per site with drag-and-drop reassignment, showing temperature class compatibility and conflicts.
3. **Arrival prediction and re-planning.** Use carrier updates and gate check-in times to predict late arrivals, then suggest a revised door and slot, and draft a message to the carrier for approval.
4. **Yard dwell report.** A weekly report by carrier and site with dwell time, late arrival rate and detention cost.

## 5. Nice-to-have features

- A driver self check-in page reachable by QR code at the gate.
- Notification to the receiving team when a truck is within 30 minutes of arrival.

## 6. Out of scope for the proof of concept

- Direct integration with the warehouse management system. The proof of concept uses a CSV of bookings and a mock inbox.
- Billing and invoice reconciliation.
- Any native mobile application.

## 7. Constraints and assumptions

- Cold chain data is commercially sensitive, so hosting must remain within the country.
- Carrier contact details are personal data and must be masked in any model prompt.
- Planners use shared desktop machines with a current browser, no installation allowed.
- Each suggested re-plan must be approved by a planner. No automated message goes to carriers.

## 8. Budget and timeline

- Approved budget for the proof of concept: 52,000, including hosting during evaluation.
- A prototype demonstration to the operations board is scheduled for 18 June.
- The pilot at the smallest site is planned for the third quarter, subject to board approval.

## 9. Success measures for the proof of concept

- Booking extraction field accuracy of at least 92 percent on 150 sample emails.
- A planner can confirm a draft booking in under 30 seconds.
- The re-planning suggestion is accepted without edits in at least 60 percent of test scenarios.

## 10. Action items

| # | Action | Owner | Due |
|---|--------|-------|-----|
| 1 | Provide 150 anonymised booking emails with the final spreadsheet entries | Lucinda Farrow, planning lead | 3 May |
| 2 | Share the door layout and temperature class rules for all three sites | Emeka Tran, site manager | 10 May |
| 3 | Confirm hosting region policy with the security officer | Rosalind Ketteridge, IT security | 12 May |
| 4 | Deliver architecture outline and cost table | Ostrava Bridge Advisory | 17 May |
| 5 | Schedule a stakeholder demonstration for the operations board | Lucinda Farrow | 30 May |

## 11. Risks

- Email formats vary widely between carriers, so extraction quality may differ by carrier. Mitigation: start with the ten highest-volume carriers.
- Planners may distrust automated suggestions. Mitigation: always show the reason and the source data for each suggestion.
- The sample data may not cover seasonal peaks. Mitigation: request a peak week sample.

## 12. Glossary

- **Dwell time:** minutes from gate entry to gate exit for a truck.
- **Temperature class:** ambient, chilled or frozen, which determines which doors and bays can be used.
- **Detention:** a charge paid to a carrier when a truck waits beyond the agreed free time.
