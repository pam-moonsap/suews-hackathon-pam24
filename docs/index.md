# UDA-city Heat Contrast Analysis

This practice run uses the UDA-city hackathon dataset: a synthetic,
lower-income, hot-humid, Colombo-like city with 10 neighbourhoods. I used the
provided SUEWS/SuPy configuration (`uda-city.yml`) and compared the present
hot-humid forcing against the supplied +2.5 C pseudo-warming scenario.

## Contrast Zones

- **Most built-up urban core:** Zheng He Towers (`gridiv 10`), building fraction
  `0.44`, green-blue fraction `0.15`.
- **Most vegetated suburban/refuge area:** Jade Gardens (`gridiv 1`), building
  fraction `0.047`, green-blue fraction `0.26`.
- **Highest risk in this run:** Kampong Lama (`gridiv 4`), using the reference
  risk bridge: `risk = minmax((hazard * exposure * vulnerability)^(1/3))`.

The meteorology is shared across neighbourhoods, so differences between zones
come from morphology, land cover, and socio-economic exposure/vulnerability.
The future forcing raises air temperature by exactly 2.5 C while keeping the
same hot-humid event structure. QF is off, so population affects risk exposure,
not model heat input.

## Diurnal Change In The High-Risk Zone

![Diurnal future-minus-present flux and T2 changes for the high-risk zone](diurnal_high_risk_zone.png)

For the high-risk zone, Kampong Lama, I first paired each present hourly value
with the same future-scenario hour and calculated `future - present` for `QN`,
`QH`, `QE`, `QS`, and `T2`. The plot then shows the diurnal mean of those
point-by-point changes after the 14-day spin-up. This makes the small energy
partition changes visible instead of hiding them behind near-overlapping curves.

## Surface Energy Balance Across Land-Cover Zones

![Surface energy balance by land-cover zone](energy_balance_landcover_zones.png)

Bars show the present-day daytime mean partitioning of surface energy for all
10 neighbourhoods, sorted from lowest to highest building fraction. QN is shown
as black markers; QH, QE, and QS are stacked to show the partition of available
energy. The green outline marks the most vegetated refuge, and the black outline
marks the most built-up core.

## Data Products

- [Hourly QH, QE, QN, QS, and T2 for present and +2.5 C runs](hourly_fluxes_t2_present_future.csv)
- [Point-by-point high-risk-zone future-minus-present deltas](hourly_deltas_high_risk_zone.csv)
- [Diurnal high-risk-zone future-minus-present deltas](diurnal_deltas_high_risk_zone.csv)
- [Land-cover zone summary](landcover_zone_summary.csv)
- [Meteorology summary](meteorology_summary.csv)
- [Risk-zone ranking](risk_zone_summary.csv)
- [Energy-balance summary](energy_balance_landcover_zones.csv)

## Honest Limits

This is a compact practice run: all 10 neighbourhoods were simulated, but the
window was limited to 14 spin-up days plus 30 analysis days to stay within the
desktop memory limit. SUEWS gives an environmental heat hazard, not a health
outcome. The socio-economic layer is synthetic, so ranks are more meaningful
than absolute values.
