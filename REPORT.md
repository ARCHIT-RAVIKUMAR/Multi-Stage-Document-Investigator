# Final Report
_Source run: runs/temp_default/run_1_

## Conclusion
Building 2 lost utility power on 14 March and Generator B then Generator A carried the load, but the report contradicts itself on start time, restoration time, customer counts, premium counts, who approved failover, UPS runtime, fuel level and cause. The root cause is not established. Most headline numbers cannot be trusted until the raw logs are checked.

## Established findings
- Building 1 was not affected by the incident. (F9)
- Both generators are rated at 2 MW. (F16)
- The utility provider was notified at 03:05 (stated in three places, consistently). (F13)
- Generator B shut down at 04:10 and Generator A took the load. (F14)
- A refuel truck was dispatched at 03:40. (F22)
- Support received 1,208 tickets. (F20)

## Unresolved conflicts
- **X1**: F1 says power was lost at 02:14 but F10 timeline shows the alarm at 02:41 - would resolve: Raw utility/monitoring logs with timestamps
- **X2**: F3 says service restored at 06:34 (4h20m outage per F4) but F15 says utility feed restored at 08:05 - would resolve: Utility and service-restoration logs
- **X3**: F5 says 312 customers affected but F19 says 213 - would resolve: Billing or support records of affected accounts
- **X4**: F6 says Priya Raman approved the failover but F12 says Daniel Okafor - would resolve: Change-approval record or on-call log
- **X5**: F2 says the UPS carried the load for 15 minutes but F11 says 9 minutes (F17 is only the rating, not a conflict) - would resolve: UPS controller event log
- **X6**: F18 says roughly 11 hours of runtime but F21 says 20 percent, about 3 hours - would resolve: Fuel vendor gauge reading vs Facilities estimate
- **X7**: F7 says a storm triggered the fault but F23 says clear skies and F24 says a transformer failure at Substation 7 - would resolve: Utility provider incident report; independent weather data
- **X8**: F19 says 41 premium customers but F25 says 38 - would resolve: Customer tier list for affected accounts

## Root cause
Determined: False
Not determined. The facts say the full root cause is under investigation; a storm and a transformer failure are both mentioned but the storm claim conflicts with the weather record.

## Not supported by the document
- Whether any customer data was lost
- Why the Substation 7 transformer failed
- Any SLA credit or financial penalty
- Why Generator B shut down at 04:10

Overall confidence: low
