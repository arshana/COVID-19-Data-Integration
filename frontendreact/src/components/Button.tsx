import React, { useEffect, useState } from 'react'

interface ButtonInterface {
    url: string;
    onClickFunction(event:React.MouseEvent<HTMLButtonElement>):void;
    buttonName: string;
}

// creates different button options to look into the data
// geoLevel = specific area of interest
// geoCode = the parameter for the different searches
export default function Button(props:ButtonInterface) {
    const [infoOutput, setInfoOutput] = useState<Object[]>([]);
    useEffect(() => {
        const updateInfoOutput =  async () => {
            const fetchedInfoOutput:Object[] = await (await fetch(props.url)).json();
            setInfoOutput(fetchedInfoOutput)
        };
        updateInfoOutput();
    }, [props.url]);
    const buttonTitle:string = (infoOutput.length === 0 ? "no current related data for this area" : "click to see data in a new tab");
    return (
            <button onClick={props.onClickFunction} disabled={infoOutput.length === 0} title={buttonTitle}>{props.buttonName}</button>
    );
}