import React from "react";
import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="h-100">
      <ul className="nav justify-content-center fixed-top py-3">
        <li className="nav-item">
          <Link className="nav-link" to="/extract_sentence">
            Extract Sentence
          </Link>
        </li>
        <li className="nav-item">
          <Link className="nav-link" to="/sync_audio">
            Sync Audio
          </Link>
        </li>
        <li className="nav-item">
          <Link className="nav-link" to="/sync_translation">
            Sync Translation
          </Link>
        </li>
      </ul>
      <div className="h-100 d-flex align-items-center justify-content-center">
        <h1>EPUB Toolkit</h1>
      </div>
    </div>
  );
};

export default Home;
