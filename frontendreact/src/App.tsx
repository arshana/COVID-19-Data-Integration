import React, {useState} from 'react'
import './App.css';
import ButtonOptions from './components/ButtonOptions';
import DropDown  from './components/DropDown';
import InteractionPanel from './components/InteractionPanel';

function App() {
  const [selectedCountry, changeCountry] = useState<string>("")
  const countryFunction = (event:React.ChangeEvent<HTMLSelectElement>):void => {
    changeCountry(event.target.value);
    changeRegion("")
    changeDistrict("")
  }
  const [selectedRegion, changeRegion] = useState<string>("")
  const regionFunction = (event:React.ChangeEvent<HTMLSelectElement>):void => {
    changeRegion(event.target.value);
    changeDistrict("")
  }
  const [selectedDistrict, changeDistrict] = useState<string>("")
  const districtFunction = (event:React.ChangeEvent<HTMLSelectElement>):void => {
    changeDistrict(event.target.value);
  }
  const selectedCountryCode:string = (selectedCountry !== "" ? selectedCountry.split("#")[1] : "");
  const selectedRegionCode:string = (selectedRegion !== "" ? selectedRegion.split("#")[1] : "");
  const selectedDistrictCode:string = (selectedDistrict !== "" ? selectedDistrict.split("#")[1] : "");
  return (
    <div className="App">
      <DropDown urlEnding='all-from-table/?table=countries' geoLevel='country' changeFunction={countryFunction}/>
      <InteractionPanel selectedGeoLevel='countries' selectedGeoCode={selectedCountryCode}
       optionsUrlEnding={'regions-from-country/?country-code=' + selectedCountryCode}
       optionsGeoLevel='region' areaFunction={regionFunction} />
      <InteractionPanel selectedGeoLevel='regions' selectedGeoCode={selectedRegionCode}
       optionsUrlEnding={'districts-from-region/?region-code=' + selectedRegionCode}
       optionsGeoLevel='district' areaFunction={districtFunction} />
       {selectedDistrictCode !== '' ? <ButtonOptions geoLevel='districts' geoCode={selectedDistrictCode}/> : null}
    </div>
  );
}



export default App;
