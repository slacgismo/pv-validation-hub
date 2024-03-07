import React from 'react';
import {
  BrowserRouter,
  Routes,
  Route,
} from 'react-router-dom';
import Register from '../Register/register.jsx';
import Login from '../Login/login.jsx';
import Header from '../GlobalComponents/Header/header.jsx';
import Homepage from '../Homepage/homepage.jsx';
import Analyses from '../Analyses/Analyses.jsx';
import Analysis from '../Analysis/Analysis.jsx';
import Submission from '../Submission/Submission.jsx';
import Profile from '../Profile/profile.jsx';
import DeveloperHome from '../Developer/Mainpage/mainpage.jsx';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Header />
        <div className="container d-flex align-items-center" style={{ position: 'absolute', top: '8%', width: '100%' }}>
          <Routes>
            <Route path="/register" element={<Register />} />
            <Route path="/login" element={<Login />} />
            <Route path="/analyses" element={<Analyses />} />
            <Route path="/analysis/:analysis_id" element={<Analysis />} />
            <Route path="/submission/:submission_id" element={<Submission />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="/developer" element={<DeveloperHome />} />
            <Route path="/" element={<Homepage />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
