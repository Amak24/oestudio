import { useState } from "react";
import API from "../api/api";

export default function RegisterForm() {
  const [form, setForm] = useState({
    username: "",
    email: "",
    password: "",
    confirm_password: "",
    is_artist: false,
  });

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm({ ...form, [name]: type === "checkbox" ? checked : value });
  };

  const handleSubmit = async e => {
    e.preventDefault();
    try {
      await API.post("/register", form);
      alert("Registered!");
    } catch {
      alert("Error on registration");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="username" placeholder="Username" onChange={handleChange} />
      <input name="email" type="email" placeholder="Email" onChange={handleChange} />
      <input name="password" type="password" placeholder="Password" onChange={handleChange} />
      <input name="confirm_password" type="password" placeholder="Confirm" onChange={handleChange} />
      <label>
        <input type="checkbox" name="is_artist" onChange={handleChange} />
        Register as Artist
      </label>
      <button type="submit">Register</button>
    </form>
  );
}