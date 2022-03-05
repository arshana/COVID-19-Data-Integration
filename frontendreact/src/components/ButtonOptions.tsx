import React, {useEffect, useState} from 'react'

interface specificLevel {
    geoLevel: string;
    geoCode: string;
}


export default function ButtonOptions(props:specificLevel) {
    const casesFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        window.open('http://127.0.0.1:8000/' + props.geoLevel + '-cases/?' + props.geoLevel + '-code=' + props.geoCode, '_blank')
    }
    const vaccinationsFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        window.open('http://127.0.0.1:8000/' + props.geoLevel + '-vaccinations/?' + props.geoLevel + '-code=' + props.geoCode, '_blank')
    }
    const strainsFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        window.open('http://127.0.0.1:8000/' + props.geoLevel + '-strains/?' + props.geoLevel + '-code=' + props.geoCode, '_blank')
    }
    const populationFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        window.open('http://127.0.0.1:8000/' + props.geoLevel + '-population/?' + props.geoLevel + '-code=' + props.geoCode, '_blank')
    }
    const agesFunction = (event:React.MouseEvent<HTMLButtonElement>):void => {
        window.open('http://127.0.0.1:8000/' + props.geoLevel + '-ages/?' + props.geoLevel + '-code=' + props.geoCode, '_blank')
    }
    return (
        <div>
            <button onClick={casesFunction}>Cases</button>
            <button onClick={vaccinationsFunction}>Vaccinations</button>
            <button onClick={strainsFunction}>Strains</button>
            <button onClick={populationFunction}>Population</button>
            <button onClick={agesFunction}>Ages</button>
        </div>
    )
}