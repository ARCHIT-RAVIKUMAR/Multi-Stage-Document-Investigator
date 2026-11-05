# Larkspur Data Center - Incident Review INC-2291
*Compiled from multiple contributors. Not yet reconciled.*

## 1. Executive Summary (J. Whitcombe, Incident Manager)
On 14 March, the Larkspur Data Center (Building 2) lost utility power at 02:14 local time. The battery UPS carried the load for 15 minutes before generators took over. Normal service was restored at 06:34, giving a total outage of 4 hours 20 minutes. In total, 312 customers were affected. Failover to Generator B was approved by Priya Raman, Operations Lead. The utility fault was triggered by a storm. The full root cause is still under investigation.

## 2. Facility Background
Building 2 opened in 2017 and houses four data halls with roughly 1,900 racks. Building 1, on the same campus, was not affected by the incident. The visitor parking lot was repaved last autumn and now has 14 additional spaces. The campus is staffed 24/7 by a rotating team of operations engineers.

## 3. Timeline (S. Doyle, compiled from monitoring logs)
- 02:41 - Monitoring raised a utility feed lost alarm for Building 2.
- 02:50 - UPS batteries, which had carried the load for 9 minutes, were exhausted and Generator B was started.
- 02:52 - Generator B online. Failover was approved by Daniel Okafor, Operations Lead.
- 03:05 - Utility provider notified.
- 04:10 - Generator B shut down; Generator A took the load.
- 08:05 - Utility feed restored and service confirmed normal for all halls.

## 4. Power Systems (Facilities, R. Nunez)
Both generators are rated at 2 MW. The UPS system is rated for 15 minutes at full load. Facilities reported that Generator B's tank held roughly 11 hours of runtime at the start of the incident. Generator A was last serviced in January. The UPS battery strings were installed in 2019.

## 5. Customer Impact (Support, A. Mbeki)
A total of 213 customers experienced degraded or no service, of which 41 were premium tier. Support received 1,208 tickets during and after the event. The median first-response time to tickets was 22 minutes.

## 6. Recovery Notes (Operations)
The fuel vendor's refuel log shows Generator B's tank at 20 percent at the start of the incident, enough for about 3 hours. A refuel truck was dispatched at 03:40. After Generator B shut down, Generator A carried the load until utility power returned. The utility provider was notified at 03:05.

## 7. Weather and Utility Context
The regional weather station recorded clear skies, no precipitation, and no wind above 12 km/h on the night of 13 to 14 March. The utility provider attributed the feed loss to a transformer failure at Substation 7. Sunrise on 14 March was at 06:12.

## 8. Miscellaneous Staff Notes
The cafeteria is switching to a new catering vendor next month; the proposed menu includes a vegetarian lasagna. The office plants on level 3 were watered on Monday. The badge printer in the lobby is out of cyan toner. The annual softball game is scheduled for June. Several engineers asked whether the night-shift parking permits could be extended.

## 9. Archive Summary
Building 2 lost utility power on 14 March. 38 premium-tier customers were affected. The utility provider was notified at 03:05. Both generators are rated at 2 MW each. The root cause is under investigation.
