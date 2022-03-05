import React, {useEffect, useState} from 'react'
import './App.css';
import DropDown  from './components/DropDown';

function App() {
  const [selectedCountry, changeCountry] = useState<string>("")
  const countryFunction = (event:React.ChangeEvent<HTMLSelectElement>):void => {
    changeCountry(event.target.value);
  }
  const selectedCountryName:string = (selectedCountry !== "" ? selectedCountry.split("#")[0] : "");
  const selectedCountryCode:string = (selectedCountry !== "" ? selectedCountry.split("#")[1] : "");
  return (
    <div className="App">
      <DropDown geoOption='countries' name='country_name' code='country_code' changeFunction={countryFunction}/>
      {selectedCountryName !== "" ? <p> Selected Country is {selectedCountryName} </p> :
                                <p> please select a country to work with</p>}
    </div>
  );
}



export default App;
