import { useState } from "react";
import API from "../api/api";

export default function ConcertForm() {
  const [form, setForm] = useState({
    title: "",
    description: "",
    video_url: "",
    thumbnail_url: "",
    genre: "rock",
    duration: "",
    is_live: false,
    scheduled_for: "",
  });

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      await API.post("/concerts/create", form);
      alert("Concert created");
    } catch {
      alert("Error creating concert");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" placeholder="Title" onChange={handleChange} />
      <textarea name="description" placeholder="Description" onChange={handleChange}></textarea>
      <input name="video_url" placeholder="Video URL" onChange={handleChange} />
      <input name="thumbnail_url" placeholder="Thumbnail URL" onChange={handleChange} />
      <select name="genre" onChange={handleChange}>
        <option value="rock">Rock</option>
        <option value="pop">Pop</option>
        <option value="jazz">Jazz</option>
      </select>
      <input name="duration" placeholder="Duration" onChange={handleChange} />
      <label>
        <input type="checkbox" name="is_live" onChange={handleChange} /> Live?
      </label>
      <input type="datetime-local" name="scheduled_for" onChange={handleChange} />
      <button type="submit">Create</button>
    </form>
  );
}
import { useState } from "react";
import API from "../api/api";

export default function ConcertForm() {
  const [form, setForm] = useState({
    title: "",
    description: "",
    video_url: "",
    thumbnail_url: "",
    genre: "rock",
    duration: "",
    is_live: false,
    scheduled_for: "",
  });

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      await API.post("/concert/create", form);
      alert("Concert created successfully!");
    } catch (error) {
      alert("Error creating concert");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="title" placeholder="Concert Title" onChange={handleChange} required />
      <textarea name="description" placeholder="Description" onChange={handleChange} required />
      <input name="video_url" placeholder="Video URL" onChange={handleChange} required />
      <input name="thumbnail_url" placeholder="Thumbnail URL" onChange={handleChange} required />
      <select name="genre" onChange={handleChange}>
        <option value="rock">Rock</option>
        <option value="pop">Pop</option>
        <option value="jazz">Jazz</option>
        <option value="classical">Classical</option>
        <option value="hiphop">Hip Hop</option>
        <option value="electronic">Electronic</option>
        <option value="folk">Folk</option>
        <option value="country">Country</option>
        <option value="indie">Indie</option>
        <option value="other">Other</option>
      </select>
      <input name="duration" placeholder="Duration (minutes)" onChange={handleChange} required />
      <label>
        <input type="checkbox" name="is_live" onChange={handleChange} />
        Live Concert
      </label>
      {form.is_live && (
        <input 
          type="datetime-local" 
          name="scheduled_for" 
          onChange={handleChange} 
        />
      )}
      <button type="submit">Create Concert</button>
    </form>
  );
}
