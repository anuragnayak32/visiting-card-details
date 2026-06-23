import { Sun, Moon, Menu, CreditCard } from "lucide-react";
import { useTheme } from "../../context/ThemeContext.jsx";

export default function Header({ title, onMenuToggle }) {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="chat-header">
      <div className="header-left">
        <button className="hamburger" onClick={onMenuToggle}>
          <Menu size={20} />
        </button>
        <div className="header-title">
          <CreditCard size={18} className="header-icon" />
          <span>{title || "Visiting Card AI"}</span>
        </div>
      </div>
      <div className="header-right">
        <button className="theme-toggle" onClick={toggleTheme} title="Toggle theme">
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </div>
    </header>
  );
}
