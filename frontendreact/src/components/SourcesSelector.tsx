import React, { useEffect, useState } from 'react'

interface SourceInterface {
    url: string
}

export default function SourceSelector(props:SourceInterface) {
    const [sourceOptions, setSourceOptions] = useState<Object[]>([]);
    useEffect(() => {
        const updateSourceOptions =  async () => {
            const fetchedSourceOutput:Object[] = await (await fetch(props.url)).json();
            setSourceOptions(fetchedSourceOutput)
        };
        updateSourceOptions();
    }, [props.url]);
    return (
        <div>{ props.url !== "" ?
            <><h2>Select any number of listed sources (you need to choose at least one)</h2><select multiple //onChange
            > {sourceOptions.map((optionItem: any) => <option key={optionItem['source_id']}
                value={optionItem['source_id'] + "#" + optionItem['source_information']}>
                {optionItem["source_information"] + " (" + optionItem["source_id"] + ")"}</option>)}
                <option value="ALL!">All available sources</option></select></>
            : null}
    </div>
    );
}