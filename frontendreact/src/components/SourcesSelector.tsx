import React, { useEffect, useState } from 'react'

interface SourceInterface {
    dataUrl: string;
    sourceUrl: string;
}
// lists the available sources to be used for the query
// given the dataUrl (to actually get the data) and
// sourceUrl which gives a list of the available sources sorted by source id 
export default function SourceSelector(props:SourceInterface) {
    const [sourceOptions, setSourceOptions] = useState<Object[]>([]);
    const checkedSources:Map<string, boolean> = new Map();
    useEffect(() => {
        const updateSourceOptions =  async () => {
            const fetchedSourceOutput:Object[] = await (await fetch(props.sourceUrl)).json();
            setSourceOptions(fetchedSourceOutput)
        };
        updateSourceOptions();
    }, [props.sourceUrl]);
    const onChangeFunction = (event:React.ChangeEvent<HTMLInputElement>):void => {
        console.log(checkedSources);
        checkedSources.set(event.target.value, !checkedSources.get(event.target.value));
        console.log(checkedSources);
    }
    const onClickFunctionAll = (event:React.MouseEvent<HTMLButtonElement>):void => {
        window.open(props.dataUrl, "_blank")
    }
    const onClickFunctionSelect = (event:React.MouseEvent<HTMLButtonElement>):void => {
        let usedSources:string = "&sources=(";
        let trueAmounts:number = 0;
        checkedSources.forEach( (value:boolean, key:string):void => {
            console.log(key + " " + value);
            if (value){
                usedSources += key + ", ";
                trueAmounts++;
            }
        });
        if (trueAmounts > 0) {
            usedSources = usedSources.substring(0, usedSources.length - 2);
        }
        usedSources += ")";
        console.log(usedSources);
        window.open(props.dataUrl + usedSources, "_blank");
    }
    return (
        <div>{ props.sourceUrl !== "" ?
            <div>
            <h2>Select any number of listed sources</h2>
            <form>
            {sourceOptions.map((optionItem: any) =>
                    <div key={optionItem['source_id']}> 
                        <label>{optionItem['source_information'] + " (" + optionItem['source_id'] + ")"}</label>
                        <input type="checkbox" onChange = {onChangeFunction} value={optionItem['source_id']}/>
                    </div>
                    )}
            </form>
            <button onClick={onClickFunctionAll} type="submit">Use all sources</button>
            <button onClick={onClickFunctionSelect} type="submit">Use selected sources</button>
            
            </div> : null}
        </div>

    );
}