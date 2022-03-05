import React, {useEffect, useState} from 'react'

interface DropDownProp {
    urlEnding: string;
    geoLevel: string;
    changeFunction(event: React.ChangeEvent<HTMLSelectElement>):void;
}



export default function DropDown(props: DropDownProp) {
    const [options, setOptions] = useState<Object[]>([]);
    useEffect(() => {
        const updateGeoOptions =  async () => {
            const fetchedOptions:Object[] = await (await fetch("http://127.0.0.1:8000/" + props.urlEnding)).json();
            setOptions(fetchedOptions)
        };
        updateGeoOptions();
    }, [props.urlEnding]);
    console.log(options);
    return (
        <div>
        <h2>Selected a listed {props.geoLevel} to work with</h2>
        <select onChange={props.changeFunction}
        > {options.map((optionItem:any) =><option key={optionItem[props.geoLevel + "_code"]}
         value={optionItem[props.geoLevel + "_name"] + "#" + optionItem[props.geoLevel + "_code"]}>
             {optionItem[props.geoLevel + "_name"] + " (" + optionItem[props.geoLevel + "_code"] + ")"}</option>)} </select>
        </div>
    );
}