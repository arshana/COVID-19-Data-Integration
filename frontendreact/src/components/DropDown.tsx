import React, {useEffect, useState} from 'react'

interface DropDownProp {
    urlEnding: string;
    geoLevel: string;
    changeFunction(event: React.ChangeEvent<HTMLSelectElement>):void;
}


// Drop down for specific geographical option,
// urlEnding = where to fetch data
// geoLevel = what specifc type of data are we looking for (ie country vs region)
// changeFunction = function that triggers when we select an option
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
        {options.length > 0 ?
            <div><h2>Select a listed {props.geoLevel} to work with</h2><select onChange={props.changeFunction}
                > {options.map((optionItem: any) => <option key={optionItem[props.geoLevel + "_code"]}
                    value={optionItem[props.geoLevel + "_name"] + "#" + optionItem[props.geoLevel + "_code"]}>
                    {optionItem[props.geoLevel + "_name"] + " (" + optionItem[props.geoLevel + "_code"] + ")"}</option>)}
                    <option value="" selected disabled hidden>Choose a given {props.geoLevel}</option></select>
            </div>
        : null}
        </div>
    );
}