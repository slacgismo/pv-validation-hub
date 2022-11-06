import Register from '../Register/register';
import Header from '../Header/header';
import Login from '../Login/login';
import {
  BrowserRouter,
  Routes,
  Route
} from "react-router-dom";
import Homepage from '../Homepage/homepage';
import Dashboard from '../Dashboard/Dashboard';
function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Header/>
        <div className="container d-flex align-items-center flex-column">
          <Routes>
            <Route path="/register" element={<Register/>}/>
            <Route path="/login" element={<Login/>}/>
            <Route path='/dashboard' element={<Dashboard/>}/>
            <Route path="/" element={<Homepage/>}/>
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;
