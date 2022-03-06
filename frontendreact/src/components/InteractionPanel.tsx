import React from 'react'
import ButtonOptions from './ButtonOptions';
import DropDown from './DropDown';

interface GeoInterface {
    selectedGeoLevel: string;
    selectedGeoCode: string;
    optionsUrlEnding: string;
    optionsGeoLevel: string;
    areaFunction(event:React.ChangeEvent<HTMLSelectElement>):void
}

// combination of Button and DropDown
// selectedGeoLevel = the user selected this area
// selectedGeoCode = the specific element of the selected level
// optionsUrlEnding = the given url to search for more options for the user to select
// optionsGeoLevel = the more specific derivative of the already selected level
export default function InteractionPanel(props:GeoInterface) {
    return(
        <div>
        {props.selectedGeoCode !== '' ? 
            <div><ButtonOptions geoLevel={props.selectedGeoLevel} geoCode={props.selectedGeoCode} />
            <DropDown urlEnding={props.optionsUrlEnding} geoLevel={props.optionsGeoLevel} changeFunction={props.areaFunction} />
            </div> 
            : null}
        </div>   
    );
}