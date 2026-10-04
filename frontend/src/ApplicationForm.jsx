import { useState } from "react";

const STATUS_OPTIONS = ["Applied", "Interview", "Offer", "Rejected"];

const EMPTY_VALUES = { company: "", position: "", status: "Applied", job_description: "" };

// One form, two jobs: pass no initialValues to create a new application,
// or pass an existing application to edit it in place.
function ApplicationForm({ initialValues, onSubmit, onCancel }) {
  // The API returns job_description: null when it was never set — swap
  // that for "" so the textarea is always a controlled input.
  const [values, setValues] = useState(() => ({
    ...EMPTY_VALUES,
    ...initialValues,
    job_description: initialValues?.job_description ?? "",
  }));
  const [errors, setErrors] = useState({});

  function handleChange(event) {
    const { name, value } = event.target;
    setValues((previous) => ({ ...previous, [name]: value }));
  }

  // Mirrors the backend's Pydantic constraints so the user sees a mistake
  // right away — the API still re-validates on its end regardless.
  function validate() {
    const nextErrors = {};
    if (!values.company.trim()) nextErrors.company = "Company is required";
    if (!values.position.trim()) nextErrors.position = "Position is required";
    return nextErrors;
  }

  function handleSubmit(event) {
    event.preventDefault();

    const validationErrors = validate();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    // Only send what the API accepts (not id / created_at), and store a
    // blank description as null rather than an empty string.
    onSubmit({
      company: values.company,
      position: values.position,
      status: values.status,
      job_description: values.job_description.trim() || null,
    });
  }

  return (
    <form className="application-form" onSubmit={handleSubmit} noValidate>
      <div className="form-field">
        <label htmlFor="company">Company</label>
        <input id="company" name="company" value={values.company} onChange={handleChange} />
        {errors.company && <span className="form-error">{errors.company}</span>}
      </div>

      <div className="form-field">
        <label htmlFor="position">Position</label>
        <input id="position" name="position" value={values.position} onChange={handleChange} />
        {errors.position && <span className="form-error">{errors.position}</span>}
      </div>

      <div className="form-field">
        <label htmlFor="status">Status</label>
        <select id="status" name="status" value={values.status} onChange={handleChange}>
          {STATUS_OPTIONS.map((status) => (
            <option key={status} value={status}>
              {status}
            </option>
          ))}
        </select>
      </div>

      <div className="form-field">
        <label htmlFor="job_description">Job description</label>
        <textarea
          id="job_description"
          name="job_description"
          rows={6}
          placeholder="Paste the posting here — the AI tools use it to tailor cover letters and match scores."
          value={values.job_description}
          onChange={handleChange}
        />
      </div>

      <div className="form-actions">
        <button type="button" className="button-secondary" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="button-primary">
          Save
        </button>
      </div>
    </form>
  );
}

export default ApplicationForm;
