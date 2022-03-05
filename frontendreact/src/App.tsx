import React, {useEffect, useState} from 'react'
import './App.css';
import ButtonOptions from './components/ButtonOptions';
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
      <DropDown urlEnding='countries/' geoLevel='country' changeFunction={countryFunction}/>
      {selectedCountryName !== "" ?
       <div> 
          <p> Selected Country is {selectedCountryName} </p> 
          <DropDown urlEnding={'country-regions/?country-code=' + selectedCountryCode} geoLevel='region' changeFunction={countryFunction} />
        </div>
       : <p> please select a country to work with</p>}
      <ButtonOptions geoLevel='country' geoCode='JP'/>
    </div>
  );
}



export default App;
