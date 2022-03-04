import React, {useEffect, useState} from 'react'
import './App.css';
import DropDown  from './components/DropDown';

function App() {
  const [selectedCountry, changeCountry] = useState<string>("")
  const countryFunction = (event:React.ChangeEvent<HTMLSelectElement>):void => {
    changeCountry(event.target.value);
  }
  return (
    <div className="App">
      <DropDown geoOption='countries' name='country_name' code='country_code' changeFunction={countryFunction}/>
      <p> This is our selected country {selectedCountry}</p>
    </div>
  );
}



export default App;
