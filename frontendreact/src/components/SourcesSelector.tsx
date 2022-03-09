import React, { useEffect, useState } from 'react'

interface SourceInterface {
    dataUrl: string;
    sourceUrl: string;
    onClickFunction(event:React.MouseEvent<HTMLButtonElement>):void
}
export default function SourceSelector(props:SourceInterface) {
    const [sourceOptions, setSourceOptions] = useState<Object[]>([]);
    // const checkedSources:Map<string, boolean> = new Map();
    useEffect(() => {
        const updateSourceOptions =  async () => {
            const fetchedSourceOutput:Object[] = await (await fetch(props.sourceUrl)).json();
            setSourceOptions(fetchedSourceOutput)
        };
        updateSourceOptions();
    }, [props.sourceUrl, props.dataUrl]);
    const onChangeFunction = (event:React.ChangeEvent<HTMLInputElement>):void => {
        // checkedSources.set(event.target.value, !checkedSources.get(event.target.value));
        // console.log(checkedSources);
    }
    return (
        <div>{ props.sourceUrl !== "" ?
            <div>
            <h2>Select any number of listed sources (you need to choose at least one)</h2>
            <form>
            {sourceOptions.map((optionItem: any) =>
                    <div key={optionItem['source_id']}> 
                        <label>{optionItem['source_information'] + " (" + optionItem['source_id'] + ")"}</label>
                        <input type="checkbox" onChange = {onChangeFunction} value={optionItem['source_id']}/>
                    </div>
                    )}
            <button onClick={props.onClickFunction}>Submit or die</button>
            </form>
            </div> : null}
        </div>

    );
}