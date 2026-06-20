// Date picker for choosing which day's habits to view. Defaults to today.

export default function DaySelector({ date, onChange }) {
  return (
    <div className="day-selector">
      <label htmlFor="day">Day</label>
      <input
        id="day"
        type="date"
        value={date}
        onChange={(e) => onChange(e.target.value)}
      />
    </div>
  );
}
