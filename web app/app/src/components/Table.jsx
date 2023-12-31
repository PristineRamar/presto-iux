import React from 'react';
import "../styles/table.css";
import numeral from 'numeral';

export default class Table extends React.Component {
    
    constructor(props){
      super(props);
      this.getHeader = this.getHeader.bind(this);
      this.getRowsData = this.getRowsData.bind(this);
      this.getKeys = this.getKeys.bind(this);
    }
    
    getKeys = function(){
      return Object.keys(this.props.data[0]);
    }
    
    getHeader = function(){
      var keys = this.getKeys();
      return keys.map((key, index)=>{
        return <th key={key}>{key}</th>
      })
    }
    
    getRowsData = function(columnsWithTextWrap){
      var items = this.props.data;
      var keys = this.getKeys();
      return items.map((row, index)=>{
        return <tr key={index}>
          <RenderRow index={index} key={index} data={row} keys={keys} columnsWithTextWrap={columnsWithTextWrap}/>
          </tr>
      })
    }
    
    render() {
      const columnsWithTextWrap = []; // Add the column names that should have text wrapping
        return (
          <div className='table-border'>
            <table>
            <thead>
              <tr>{this.getHeader()}</tr>
            </thead>
            <tbody>
              {this.getRowsData(columnsWithTextWrap)}
            </tbody>
            </table>
          </div>
          
        );
    }
}

const RenderRow = (props) => {
  return props.keys.map((key, index) => {
      const columnValue = props.data[key];
      const shouldWrapText = props.columnsWithTextWrap.includes(key);
      let cellContent;

      if (typeof columnValue === 'number') {
        const isNumber = true
        const hasDecimalPart = columnValue % 1 !== 0;

        if (hasDecimalPart) {
          if ((key.includes('Margin%')))
          {
            cellContent = (columnValue * 100).toFixed(0) + '%'; 
          } else if (key.includes('Income') || (key.includes('Sales') || key.includes('Margin'))) {
            cellContent = '$' + columnValue.toFixed(0); // Display up to 2 decimal places
            cellContent = numeral(columnValue).format('$0,0');
          }
          else if ((key.includes('Cost') || (key.includes('Price'))))
          {
            cellContent = '$' + columnValue.toFixed(2); // Display up to 2 decimal places
            cellContent = numeral(columnValue).format('$0,0.00');
          } else 
            cellContent = columnValue.toFixed(2); // Display up to 2 decimal places
        } else {
          if ((key.includes('Margin%')))
          {
            cellContent = (columnValue * 100).toFixed(0) + '%'; 
          } else if (key.includes('Income') || (key.includes('Sales') || key.includes('Margin'))) {
            cellContent = '$' + columnValue.toFixed(0); // Display up to 2 decimal places
            cellContent = numeral(columnValue).format('$0,0');
          }
          else if ((key.includes('Cost') || (key.includes('Price'))))
          {
            cellContent = '$' + columnValue.toFixed(2); // Display up to 2 decimal places
            cellContent = numeral(columnValue).format('$0,0');
          } 
          else if(!key.includes('Year')){              
            cellContent = numeral(columnValue).format('0,0');
          }
          else {
            cellContent = columnValue.toString();
          }
        }

        return (
          <td
              key={`row-${props.index}-col-${key}`}
              className={`${shouldWrapText ? 'wrap-text' : ''} ${isNumber ? 'center-align' : ''}`}
          >
              {cellContent}
          </td>
      );
      } else {
          return (
            <td
                key={props.data[key]}
                className={shouldWrapText ? 'wrap-text' : ''}
            >
                {columnValue}
            </td>
        );
      }
  });
}
