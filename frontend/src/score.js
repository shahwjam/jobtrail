// Green / amber / red bands for match score badges and meters.
export function scoreBand(score) {
  if (score >= 75) return "high";
  if (score >= 50) return "medium";
  return "low";
}
