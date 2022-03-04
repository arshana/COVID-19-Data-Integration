import React, {useEffect, useState} from 'react'

interface DropDownProp {
    geoOption: string;
    name: string;
    code: string;
}


export default function DropDown(props: DropDownProp) {
    const [options, setOptions] = useState<Object[]>([]);
    useEffect(() => {
        const updateGeoOptions =  async () => {
            const fetchedOptions:Object[] = await (await fetch("http://127.0.0.1:8000/" + props.geoOption + "/")).json();
            setOptions(fetchedOptions)
        };
        updateGeoOptions();
    }, [props.geoOption]);
    console.log(options);
    return (
        <select> {options.map((optionItem:any) =><option key={optionItem[props.code]}
         value={optionItem[props.name]}>{optionItem[props.name] + " (" + optionItem[props.code] + ")"}</option>)} </select>
    );
}