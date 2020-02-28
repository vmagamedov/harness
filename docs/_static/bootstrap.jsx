import React, {useState} from 'react';
import ReactDOM from 'react-dom';

import Prism from 'prismjs';
import 'prismjs/components/prism-protobuf';
import 'prismjs/themes/prism.css';

import {TypeInfo} from './typeinfo';

const LANGUAGES = [
  {value: 'python', title: 'Python'},
];

const WireType = {
    Input: 1,
    Output: 2,
};

const Accessibility = {
  Local: 'LOCAL',
  Namespace: 'NAMESPACE',
  Cluster: 'CLUSTER',
  External: 'EXTERNAL',
};

const Visibility = {
  Private: "PRIVATE",
  Headless: "HEADLESS",
  Internal: "INTERNAL",
  Public: "PUBLIC",
};

function useSetter(setter) {
  return (event) => {
    setter(event.target.value)
  }
}

function itemSetter(value, setValue, i, name) {
  return (itemValue) => {
    setValue([
      ...value.slice(0, i),
      {...value[i], [name]: itemValue},
      ...value.slice(i + 1),
    ]);
  }
}

function itemDeleter(value, setValue, i) {
  return () => {
    setValue([
      ...value.slice(0, i),
      ...value.slice(i + 1),
    ]);
  }
}

function formatField(i, wire, options) {
  return `${wire.config} ${wire.configName} = ${i} [\n        ${options.join(',\n        ')}\n    ];`;
}

function formatInput(i, wire, deployEnabled) {
  let options = [`(harness.wire).input = "${wire.value}"`];
  if (deployEnabled && wire.accessibility.length > 0) {
    options.push(`(harness.wire).access = ${wire.accessibility}`);
  }
  return formatField(i, wire, options);
}

function formatOutput(i, wire, deployEnabled) {
  let options = [`(harness.wire).output = "${wire.value}"`];
  if (deployEnabled && wire.visibility.length > 0) {
    options.push(`(harness.wire).visibility = ${wire.visibility}`);
  }
  return formatField(i, wire, options);
}

function collectImports(inputs, outputs) {
  const items = new Set(['harness/wire.proto']);
  inputs.map(w => items.add(w.configProto));
  outputs.map(w => items.add(w.configProto));
  return Array.from(items).sort();
}

function renderConfig(serviceName, deployEnabled, repository, inputs, outputs) {
  const imports = collectImports(inputs, outputs);

  let sourceLines = [
    `syntax = "proto3";`,
    '',
    `package ${serviceName};`,
  ];
  sourceLines.push('');
  imports.map(value => sourceLines.push(`import "${value}";`));
  sourceLines.push('');
  sourceLines.push(`message Configuration {`);
  sourceLines.push(`    option (harness.service).name = "${serviceName}";`);
  if (deployEnabled) {
    sourceLines.push(`    option (harness.service).container.repository = "${repository}";`);
  }
  if (inputs.length > 0 || outputs.length > 0) {
    sourceLines.push('');
  }
  let fieldNumber = 1;
  inputs.map(w => {
    sourceLines.push(`    ${formatInput(fieldNumber, w, deployEnabled)}`);
    fieldNumber++;
  });
  outputs.map(w => {
    sourceLines.push(`    ${formatOutput(fieldNumber, w, deployEnabled)}`);
    fieldNumber++;
  });
  sourceLines.push('}');

  return Prism.highlight(
    sourceLines.join('\n'),
    Prism.languages.protobuf,
    'protobuf',
  );
}

function Input(props) {
  const hasAccessibility = props.deployEnabled && TypeInfo.hasOwnProperty(props.wire.config);
  return (
    <div className="bootstrap-value bootstrap-wire">
      <span className="bootstrap-wire-value">{props.wire.value}</span>
      <div className="bootstrap-wire-inputs">
        <input className="bootstrap-wire-name" placeholder="name" type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
        <select value={props.wire.accessibility} onChange={useSetter(props.setAccessibility)} disabled={!hasAccessibility}>
          <option key={-1} value="">---</option>
          {Object.entries(Accessibility).map(([key, value]) => {
            return <option key={value} value={value}>{key}</option>
          })}
        </select>
        <button onClick={props.delete}>Delete</button>
      </div>
    </div>
  )
}

function Output(props) {
  const hasVisibility = props.deployEnabled && TypeInfo.hasOwnProperty(props.wire.config);
  return (
    <div className="bootstrap-value bootstrap-wire">
      <span className="bootstrap-wire-value">{props.wire.value}</span>
      <div className="bootstrap-wire-inputs">
        <input className="bootstrap-wire-name" placeholder="name" type="text" value={props.wire.configName} onChange={useSetter(props.setConfigName)}/>
        <select value={props.wire.visibility} onChange={useSetter(props.setVisibility)} disabled={!hasVisibility}>
          <option key={-1} value="">---</option>
          {Object.entries(Visibility).map(([key, value]) => {
            return <option key={value} value={value}>{key}</option>
          })}
        </select>
        <button onClick={props.delete}>Delete</button>
      </div>
    </div>
  )
}

function AddWireDialog(props) {
  const [wire, setWire] = useState("");

  function addWire(event) {
    props.addWire(wire);
  }

  return <div className={props.className}>
    <select value={wire} onChange={useSetter(setWire)}>
      <option key={-1} value="">--- select ---</option>
      {props.wires.map((wire, i) => {
        return <option key={i} value={wire.value}>{wire.value}</option>
      })}
    </select>
    <button onClick={addWire} disabled={wire === ""}>Add</button>
  </div>
}

function collectRequirements(inputs, outputs) {
  const items = new Set(['harness']);
  inputs.map(w => {
    w.requirements.map(v => items.add(v));
  });
  outputs.map(w => {
    w.requirements.map(v => items.add(v));
  });
  return Array.from(items).sort();
}

function Bootstrap(props) {
  const wires = props.wiresData.map((w) => {
    return {
      ...w,
      type: (w.type === 'input'? WireType.Input: WireType.Output),
    }
  });

  const [serviceName, setServiceName] = useState('');
  const [runtime, setRuntime] = useState('python');

  const [deployEnabled, setDeployEnabled] = useState(true);
  const [repository, setRepository] = useState('');

  const [inputs, setInputs] = useState([]);
  const [outputs, setOutputs] = useState([]);

  function addInput(wire) {
    const accessibility = TypeInfo.hasOwnProperty(wire.config)? Accessibility.Cluster: '';
    setInputs([...inputs, {
      ...wire,
      configName: '',
      accessibility: accessibility,
    }]);
  }

  function addOutput(wire) {
    const visibility = TypeInfo.hasOwnProperty(wire.config)? Visibility.Internal: '';
    setOutputs([...outputs, {
      ...wire,
      configName: '',
      visibility: visibility,
    }]);
  }

  function addWire(name) {
    const wire = wires.find(wire => wire.value === name);
    if (wire.type === WireType.Input) {
      addInput(wire);
    } else if (wire.type === WireType.Output) {
      addOutput(wire);
    } else {
      throw `Unknown wire type: ${wire.type}`
    }
  }

  let configMarkup = {__html: renderConfig(
    serviceName, deployEnabled, repository, inputs, outputs,
  )};

  const requirements = collectRequirements(inputs, outputs);

  return (
    <div className="bootstrap">
      <div className="bootstrap-row">
        <label className="bootstrap-key">Service Name</label>
        <input className="bootstrap-value" type="text" placeholder="bazinga" value={serviceName} onChange={useSetter(setServiceName)}/>
      </div>
      <div className="bootstrap-row">
        <label className="bootstrap-key">Runtime</label>
        <div className="bootstrap-value">
          {LANGUAGES.map(({value, title}) => {
            return (
              <label key={value}>
                <input type="radio" value={value}
                       checked={value === runtime}
                       onChange={useSetter(setRuntime)}/>
                {title}
              </label>
            )
          })}
        </div>
      </div>
      <div className="bootstrap-row">
        <label className="bootstrap-key">Deployment</label>
        <label className="bootstrap-value">
          <input type="checkbox" checked={deployEnabled} onChange={() => {setDeployEnabled(!deployEnabled)}}/>
          Enable
        </label>
      </div>
      {deployEnabled && <div className="bootstrap-row">
        <label className="bootstrap-key">Docker Image Repository</label>
        <input className="bootstrap-value" type="text" placeholder="registry.local/group/project" value={repository} onChange={useSetter(setRepository)}/>
      </div>}
      <div className="bootstrap-row">
        <label className="bootstrap-key">Add Wire</label>
        <AddWireDialog className="bootstrap-value" wires={wires} addWire={addWire} />
      </div>
      <div>
        {inputs.map((w, i) => {
          return <div className="bootstrap-row" key={i}>
            <label className="bootstrap-key">Input</label>
            <Input wire={w}
                   deployEnabled={deployEnabled}
                   setConfigName={itemSetter(inputs, setInputs, i, 'configName')}
                   setAccessibility={itemSetter(inputs, setInputs, i, 'accessibility')}
                   delete={itemDeleter(inputs, setInputs, i)}/>
          </div>
        })}
      </div>
      <div>
        {outputs.map((w, i) => {
          return <div className="bootstrap-row" key={i}>
            <label className="bootstrap-key">Output</label>
            <Output wire={w}
                    deployEnabled={deployEnabled}
                    setConfigName={itemSetter(outputs, setOutputs, i, 'configName')}
                    setVisibility={itemSetter(outputs, setOutputs, i, 'visibility')}
                    delete={itemDeleter(outputs, setOutputs, i)}/>
          </div>
        })}
      </div>
      <div>
        <h3>Configuration</h3>
        <div>
          <pre dangerouslySetInnerHTML={configMarkup}/>
        </div>
      </div>
      <div>
        <h3>Requirements</h3>
        <pre>{requirements.join('\n')}</pre>
      </div>
    </div>
  )
}

const mountPoint = document.getElementById('placeholder');
const wiresDataElement = document.getElementById('wires-data');
const wiresData = JSON.parse(wiresDataElement.innerText);
ReactDOM.render(<Bootstrap wiresData={wiresData}/>, mountPoint);
