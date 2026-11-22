# Technical Requirements Document: Last-Mile Route Re-Optimiser

**Client:** Quickroute Couriers (fictional)
**Author:** Delphine Mortlake, head of engineering
**Status:** Request for a proof of concept
**Contact:** engineering@quickroute.example.com

## Overview

Quickroute is a regional parcel courier with 140 vans and about 9,000 deliveries a day in dense urban areas. Routes are planned the night before by a routing tool. During the day, traffic, failed deliveries and same-day pickups make the plan obsolete, and dispatchers fix it by phone. We want a prototype that re-optimises routes during the day and explains its changes to dispatchers. This is a logistics and delivery problem.

## Current system

- Nightly route planning in a commercial routing tool with a CSV export of stops, time windows and vehicle assignments.
- Driver app showing a static list of stops, reporting status events (delivered, failed, delayed) to a REST endpoint.
- Dispatch console with 6 operators who phone drivers to change the order of stops.
- Vehicle positions every 30 seconds from the in-van tracker.

## Functional requirements

### R1. Live route health

The system shall calculate, per van, whether the remaining stops can be completed inside their time windows, given the current position, traffic estimate and average service time per stop. It shall show vans as green, amber or red.

### R2. Re-optimisation suggestions

When a van turns amber or red, or when a failed delivery or a same-day pickup arrives, the system shall propose a new stop order, or a transfer of stops to another van, with the expected change in on-time deliveries and distance driven.

### R3. Dispatcher approval and explanation

A dispatcher shall approve, edit or reject every suggestion. Each suggestion shall include a short plain-language reason, for example "Van 42 is 25 minutes behind because of the closure on the ring road; moving 4 stops to Van 17 saves 3 late deliveries".

### R4. Customer delay notices

For parcels likely to miss their window, the system shall draft a short message to the customer, for approval by the dispatcher, with a revised estimated window.

### R5. Daily performance summary

A daily summary of on-time rate, failed delivery rate, kilometres driven and number of suggestions accepted, by depot.

## Non-functional requirements

- Suggestions within 20 seconds of a triggering event.
- The prototype shall handle 150 vans and 10,000 stops in a simulated day.
- The prototype shall run on a single cloud virtual machine and shall not require access to the production driver app.
- Personal data of recipients (names, addresses, phone numbers) shall be masked in any request to a language model.
- Audit log of every suggestion and decision, kept for 12 months.

## Data

- A synthetic or anonymised week of historical routes with stop outcomes, provided by Quickroute.
- A traffic delay feed. For the proof of concept, a recorded sample is acceptable.
- Depot locations and van capacities as a CSV.

## Out of scope

- Replacing the nightly planner.
- Driver-facing changes. Dispatchers remain the only users of the prototype.
- Payment, billing and proof-of-delivery photos.

## Budget and schedule

- Budget for the proof of concept: 38,000 pounds, fixed price.
- Kick-off in the first week of September. Demonstration to the board on 14 November.
- A decision on a pilot at one depot is expected in December.

## Acceptance criteria

1. In a simulated day with injected disruptions, the suggestions raise the on-time delivery rate by at least 4 percentage points over the baseline of no intervention.
2. At least 70 percent of suggestions are judged acceptable by two experienced dispatchers in a blind review.
3. All suggestions include a reason and are logged.

## Action items

- Delphine Mortlake to provide the anonymised route history and depot CSV by 20 September.
- Wendell Achterberg (lead dispatcher) to review suggestion wording and join two review sessions in October.
- Quickroute IT (Sorcha Linnell) to confirm the tracker data format by 15 September.
- The supplier to deliver an architecture outline and a fixed-price statement of work by 12 September.

## Open questions

1. Should same-day pickups always take priority over scheduled deliveries?
2. How much overtime is a dispatcher allowed to propose for a driver?
3. Is the traffic feed licence permitted for use in a prototype?
