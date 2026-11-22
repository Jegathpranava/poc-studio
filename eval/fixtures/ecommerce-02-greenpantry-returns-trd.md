# Technical Requirements Document: Returns and Substitution Assistant

**Client:** Green Pantry Grocers (fictional)
**Author:** Alasdair Penhallow, product owner for online
**Status:** Proof of concept request
**Contact:** online@greenpantry.example.com

## 1. Summary

Green Pantry is an online grocery retailer delivering to 60,000 households. This request covers an e-commerce assistant that handles two high-volume problems: product substitutions when an item is out of stock at picking time, and refund or return claims for missing, damaged or poor-quality items. Today both are handled by humans in a support queue and by picker judgement.

## 2. Problem

- About 8 percent of order lines are out of stock at picking. Pickers choose a substitute by judgement, and 1 in 5 substitutions is rejected by the customer.
- Refund claims average 3,400 a week. Agents check the order, the photo and the policy, which takes about 6 minutes per claim.
- Customers with dietary restrictions (allergen, vegan, gluten free) have the worst experience when a substitute violates their preferences.
- Refund policy is applied inconsistently between agents, and the finance team estimates about 4 percent of refunds are overpaid.

## 3. Functional requirements

### 3.1 Smart substitution ranking

At picking time, when an item is unavailable, the system shall rank in-stock alternatives for that customer using price, size, brand preference, dietary profile and the customer's past accepted substitutions. The picker app shows the top three with a short reason.

### 3.2 Preference-safe rules

The system shall never suggest a substitute that conflicts with a stored dietary restriction, regardless of ranking. This rule is checked in code, not left to the language model.

### 3.3 Claim triage

For each refund claim, the system shall read the order, the customer message and any photo, classify the claim (missing, damaged, expired, wrong item, quality), check it against the refund policy, and recommend approve, partial refund or escalate, with the reason.

### 3.4 Agent review console

Agents shall see the recommendation, the evidence and the policy clause, and approve or change it with one click. Claims under 15 dollars with high confidence may be auto-approved after the pilot, but not in the proof of concept.

### 3.5 Customer reply drafting

The system shall draft a friendly reply for the agent to review, in the brand voice.

### 3.6 Reporting

A weekly report of substitution acceptance rate, refund cost per order and agent handling time.

## 4. Non-functional requirements

- Substitution ranking in under 2 seconds per item.
- Claim triage in under 15 seconds.
- Customer names, addresses and phone numbers are masked before any call to a language model.
- Images are processed only inside the cloud account of the retailer.
- Every recommendation and every human decision is logged.

## 5. Data supplied for the proof of concept

- Product catalogue of 9,000 items with attributes, allergens and stock levels (CSV).
- 12 months of anonymised substitution outcomes (accepted or rejected).
- 2,000 anonymised refund claims with the agent decision.
- The refund policy as a text document.

## 6. Budget and timing

- Fixed budget for the proof of concept: 42,000 dollars, including cloud costs.
- Prototype demo scheduled for the last week of July, before the autumn campaign planning.
- A pilot with 5 percent of orders is expected in the autumn if the demo meets the success measures.

## 7. Success measures

- Substitution acceptance rate raised from 80 percent to at least 88 percent on a replay of historical data.
- Claim triage agreement with experienced agents of at least 85 percent.
- Zero suggestions that violate a stored dietary restriction in 500 test cases.
- Agent handling time reduced from 6 minutes to under 3 minutes in a timed trial.

## 8. Action items

- Alasdair Penhallow to deliver the catalogue, outcomes and claims datasets by 2 June.
- Philippa Gantry (head of customer care) to nominate three agents for a timed trial in July.
- Ravindra Okafor-Hale (finance) to supply the refund policy and the list of overpayment patterns by 9 June.
- The supplier to provide the architecture outline, a model cost table and a mock-up of the agent console by 16 June.

## 9. Open questions

1. How should the system handle loyalty tier customers who receive more generous refunds?
2. Can photos be retained for 30 days only?
3. Does the picker app allow a third-party panel or must it be a link out?
