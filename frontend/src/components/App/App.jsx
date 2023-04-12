import Register from '../Register/register';
import Login from '../Login/login';
import Header from '../GlobalComponents/Header/header'
import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";
import Homepage from '../Homepage/homepage';
import Analyses from '../Analyses/Analyses';
import Analysis from '../Analysis/Analysis';
import Submission from '../Submission/Submission';
import Profile from '../Profile/profile';
import DeveloperHome from '../Developer/Mainpage/mainpage';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
          <Header />
          <div className="container d-flex align-items-center" style={{ position: 'absolute', top: '8%', width: '100%' }}>
            <Routes>
              <Route path="/register" element={<Register/>}/>
              <Route path="/login" element={<Login/>}/>
              <Route path='/analyses' element={<Analyses/>}/>
              <Route path='/analysis/:analysis_id' element={<Analysis/>}/>
              <Route path='/submission/:submission_id' element={<Submission/>}/>
              <Route path="/profile/:user_id" element={<Profile/>}/>
              <Route path="/developer" element={<DeveloperHome/>}/>
              <Route path="/" element={<Homepage/>}/>
            </Routes>
          </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
