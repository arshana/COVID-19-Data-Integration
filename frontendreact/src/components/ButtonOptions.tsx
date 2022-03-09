import React, {useState} from 'react'
import Button from './Button';
import SourcesSelector from './SourcesSelector';

interface specificLevel {
    geoLevel: string;
    geoCode: string;
}

// creates different button options to look into the data
// geoLevel = specific area of interest
// geoCode = the parameter for the different searches
export default function ButtonOptions(props:specificLevel) {
    const casesUrl:string = 'http://127.0.0.1:8000/info-from-area/?area=' + props.geoLevel + '&info-type=cases&area-code=' + props.geoCode;
    const vaccinationsUrl:string = 'http://127.0.0.1:8000/info-from-area/?area=' + props.geoLevel + '&info-type=vaccinations&area-code=' + props.geoCode;
    const strainsUrl:string = 'http://127.0.0.1:8000/info-from-area/?area=' + props.geoLevel + '&info-type=strains&area-code=' + props.geoCode;
    const populationUrl:string = 'http://127.0.0.1:8000/info-from-area/?area=' + props.geoLevel + '&info-type=population&area-code=' + props.geoCode;
    const ageUrl:string = 'http://127.0.0.1:8000/info-from-area/?area=' + props.geoLevel + '&info-type=age&area-code=' + props.geoCode;
    const casesSourceUrl:string = 'http://127.0.0.1:8000/sources-from-info-and-area/?area=' + props.geoLevel + '&info-type=cases&area-code=' + props.geoCode;
    const vaccinationsSourceUrl:string = 'http://127.0.0.1:8000/sources-from-info-and-area/?area=' + props.geoLevel + '&info-type=vaccinations&area-code=' + props.geoCode;
    const strainsSourceUrl:string = 'http://127.0.0.1:8000/sources-from-info-and-area/?area=' + props.geoLevel + '&info-type=strains&area-code=' + props.geoCode;
    const populationSourceUrl:string = 'http://127.0.0.1:8000/sources-from-info-and-area/?area=' + props.geoLevel + '&info-type=population&area-code=' + props.geoCode;
    const ageSourceUrl:string = 'http://127.0.0.1:8000/sources-from-info-and-area/?area=' + props.geoLevel + '&info-type=age&area-code=' + props.geoCode;
    const [chosenUrl, setChosenUrl] = useState<string>("");
    const [sourceUrl, setSourceUrl] = useState<string>("");
    const casesFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        setChosenUrl(casesUrl);
        setSourceUrl(casesSourceUrl);
    }
    const vaccinationsFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        setChosenUrl(vaccinationsUrl);
        setSourceUrl(vaccinationsSourceUrl);
    }
    const strainsFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        setChosenUrl(strainsUrl);
        setSourceUrl(strainsSourceUrl);
    }
    const populationFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        setChosenUrl(populationUrl);
        setSourceUrl(populationSourceUrl);
    }
    const agesFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        setChosenUrl(ageUrl);
        setSourceUrl(ageSourceUrl);
    }
    const onClickFunctionz = (event:React.MouseEvent<HTMLButtonElement>):void => {
        console.log("please work");
    }
    return (
        <div>
            <div>
                <h4>Push these buttons to get data related to your selected {props.geoLevel}</h4>
                <Button onClickFunction={casesFunction} url={casesUrl} buttonName='cases'/>
                <Button onClickFunction={vaccinationsFunction} url={vaccinationsUrl} buttonName='vaccinations'/>
                <Button onClickFunction={strainsFunction} url={strainsUrl} buttonName='strains'/>
                <Button onClickFunction={populationFunction} url={populationUrl} buttonName='population'/>
                <Button onClickFunction={agesFunction} url={ageUrl} buttonName='age'/>
            </div>
            <SourcesSelector dataUrl = {chosenUrl} sourceUrl = {sourceUrl} onClickFunction={onClickFunctionz} />
        </div>
    );
}