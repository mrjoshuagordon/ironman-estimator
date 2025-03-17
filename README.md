# Triathlon Race Predictor – AI-Powered Strava Integration

## Overview  
**Triathlon Race Predictor** is an app that provides **automated, AI-driven race performance estimates** for Ironman (140.6) and Ironman 70.3 events. By analyzing an athlete's **historical swim, bike, and run data** from Strava, the app applies performance modeling techniques to predict race outcomes and provide **instant feedback on improvements**.

## Problem Statement  
Triathletes often struggle to estimate their **overall race performance** when training separately in swimming, biking, and running.  
- Strava and other training platforms provide **individual workout analytics** but **lack integrated triathlon-specific race predictions**.  
- No existing tools **automatically calculate race finish time estimates** based on real-world training data.  
- Many athletes train without coaches and would benefit from **AI-driven insights** to track progress.

## Solution  
The app analyzes an athlete’s training using the **Strava API** and advanced **performance modeling** to:  
1. **Build a Baseline Profile:** Extracts 6–12 months of **swim, bike, and run data**.  
2. **Estimate LT2 for Each Sport:**  
   - Cycling: Uses **Critical Power (CP) model**.  
   - Running: Uses **VDOT-based modeling**.  
   - Swimming: Uses **CSS (Critical Swim Speed) model**.  
3. **Assess Training Durability:** Applies **fatigue modeling** to create a **custom durability score**.  
4. **Predict Ironman & 70.3 Finish Times:** Estimates race performance based on training data trends.  
5. **Automated Strava Updates:** Posts **real-time race estimate improvements** to the athlete's Strava activity description after key workouts.  

## How It Works  
1. **User Authorization via Strava**  
   - Athletes link their Strava account by clicking:  
     ```
     https://www.strava.com/oauth/authorize?client_id=143557&redirect_uri=https://precisemultisport.com&response_type=code&scope=read,activity:read_all
     ```
   - This grants read access to **all past swim, bike, and run activities**.

2. **Data Processing & AI Analysis**  
   - Backend **parses all workouts** from Strava.  
   - CP, VDOT, and CSS models estimate **LT2 performance**.  
   - A **fatigue model** refines the athlete's **durability score**.  
   - AI predicts **Ironman 70.3 & 140.6 finish times**.  

3. **Automated Race Estimate Feedback**  
   - After **key workouts**, the app **posts updates** to the athlete’s Strava activity, e.g.:  
     > "🚀 Your estimated Ironman 70.3 time improved by 5 minutes based on your latest training!"  
   - Weekly emails provide **detailed progress tracking**.

## Business Model & Growth Strategy  
### Free-to-Use Model  
✅ **Completely free** for athletes to get race estimates.  
✅ Acts as a **lead generation funnel** for coaching services.  
✅ Builds **brand awareness** for our coaching team.  

### Future Expansion  
✅ **Premium Features:** Advanced analytics, race pacing strategies, and deeper insights.  
✅ **Scalability:** More users = More data = More accurate predictions.  
✅ **Partnerships:** Strava clubs, race organizers, and gear companies.  

## Current Development Status  
✅ **Strava API integration** is functional.  
✅ **Running VDOT/threshold model** is implemented.  
✅ **Basic CP model for cycling** is in place.  
🛠 **Work in Progress:**  
   - Backend architecture improvements.  
   - Model validation and testing.  
   - UX design and user onboarding flow.  
   - Unit tests and performance refinements.  

## Next Steps  
1. **Complete Backend & Modeling Validation**  
2. **Build Simple User Interface for Race Estimates**  
3. **Test with Beta Users (10–20 Triathletes)**  
4. **Launch & Collect User Feedback**  
5. **Expand Features & Marketing**  

---

### 🚀 Want to Try It?  
If you're a triathlete and want early access, sign up at **[precisemultisport.com](https://precisemultisport.com)** or connect via **Strava OAuth Link** above.  

---
**Built by:** Precise Multisport
🏊‍♂️🚴‍♂️🏃‍♂️ **AI-Powered Insights for Smarter Training!**
