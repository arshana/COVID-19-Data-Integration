import React, {useEffect, useState} from 'react'
import axios from 'axios';

interface DropDownProp {
    geoOption: string;
}
export default function DropDown(props: DropDownProp) {
    const [options, setOptions] = useState<string[]>([]);
    useEffect(() => {
        const updateGeoOptions =  async (geoOption: string) => {
            console.log('127.0.0.1:8000/' + geoOption);
            const fetchedOptions = await axios
            .get<any>("http://127.0.0.1:8000/countries/");
            console.log(fetchedOptions);
        };
        updateGeoOptions(props.geoOption)
    }, [props.geoOption]);
    return (
        <p> a </p>
    );
}